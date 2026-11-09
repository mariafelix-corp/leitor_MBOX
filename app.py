
import io, os, re, tarfile, tempfile, zipfile, html
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime, parseaddr
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Leitor de Takeout", layout="wide")
PAGE = 25
CSP = "<meta http-equiv='Content-Security-Policy' content=\"default-src 'none'; style-src 'unsafe-inline'; img-src data:;\">"


def extrair_mbox(upload, destino):
    nome = upload.name.lower()
    bruto = os.path.join(destino, "upload.bin")
    with open(bruto, "wb") as f:
        while True:
            bloco = upload.read(8 * 1024 * 1024)
            if not bloco:
                break
            f.write(bloco)
    if nome.endswith(".mbox"):
        return [bruto]
    saidas = []
    if nome.endswith(".zip"):
        with zipfile.ZipFile(bruto) as z:
            for i in z.infolist():
                if i.filename.lower().endswith(".mbox"):
                    p = os.path.join(destino, f"m{len(saidas)}.mbox")
                    with z.open(i) as o, open(p, "wb") as d:
                        while True:
                            b = o.read(8 * 1024 * 1024)
                            if not b:
                                break
                            d.write(b)
                    saidas.append(p)
    elif nome.endswith((".tgz", ".tar.gz")):
        with tarfile.open(bruto, "r:gz") as t:
            for m in t:
                if m.isfile() and m.name.lower().endswith(".mbox"):
                    p = os.path.join(destino, f"m{len(saidas)}.mbox")
                    with t.extractfile(m) as o, open(p, "wb") as d:
                        while True:
                            b = o.read(8 * 1024 * 1024)
                            if not b:
                                break
                            d.write(b)
                    saidas.append(p)
    os.remove(bruto)
    return saidas


def indexar(caminho):
    offs = []
    anterior_vazia = True
    with open(caminho, "rb") as f:
        pos = 0
        for linha in f:
            if linha.startswith(b"From ") and (anterior_vazia or not offs):
                offs.append(pos)
            anterior_vazia = linha.strip() == b""
            pos += len(linha)
        fim = pos
    itens = []
    with open(caminho, "rb") as f:
        for i, o in enumerate(offs):
            f.seek(o)
            cab = f.read(65536)
            cab = cab.split(b"\n", 1)[1] if b"\n" in cab else cab
            sep = re.search(rb"\r?\n\r?\n", cab)
            cab = cab[: sep.start()] if sep else cab
            m = BytesParser(policy=policy.default).parsebytes(cab, headersonly=True)
            try:
                dt = parsedate_to_datetime(str(m["date"]))
            except Exception:
                dt = None
            nome, end = parseaddr(str(m["from"] or ""))
            itens.append({
                "ini": o,
                "fim": offs[i + 1] if i + 1 < len(offs) else fim,
                "assunto": str(m["subject"] or "(sem assunto)"),
                "de": nome or end or "(desconhecido)",
                "data": dt,
                "rotulos": [r.strip() for r in str(m["x-gmail-labels"] or "").split(",") if r.strip()],
            })
    return itens


def carregar_msg(caminho, it):
    with open(caminho, "rb") as f:
        f.seek(it["ini"])
        dados = f.read(it["fim"] - it["ini"])
    dados = dados.split(b"\n", 1)[1]
    return BytesParser(policy=policy.default).parsebytes(dados)


def corpo_html(msg):
    parte = msg.get_body(preferencelist=("html", "plain"))
    if parte is None:
        return "<p><i>(sem corpo)</i></p>"
    try:
        txt = parte.get_content()
    except Exception:
        txt = parte.get_payload(decode=True).decode("utf-8", "replace")
    if parte.get_content_type() == "text/plain":
        txt = "<pre style='white-space:pre-wrap;font-family:sans-serif'>" + html.escape(txt) + "</pre>"
    return CSP + txt


def fmt(dt):
    return dt.strftime("%d/%m/%Y %H:%M") if dt else ""


st.title("Leitor de e-mails do Google Takeout")

if "msgs" not in st.session_state:
    up = st.file_uploader("Importar arquivo (.mbox, .zip ou .tgz do Takeout)", type=["mbox", "zip", "tgz", "gz"])
    if up and st.button("Importar", type="primary"):
        pasta = tempfile.mkdtemp(prefix="takeout_")
        with st.spinner("Importando e indexando..."):
            arqs = extrair_mbox(up, pasta)
            if not arqs:
                st.error("Nenhum arquivo .mbox encontrado.")
                st.stop()
            todos = []
            for a in arqs:
                for it in indexar(a):
                    it["arq"] = a
                    todos.append(it)
            todos.sort(key=lambda x: x["data"].timestamp() if x["data"] else 0, reverse=True)
        st.session_state.msgs = todos
        st.session_state.pasta = pasta
        st.rerun()
    st.stop()

msgs = st.session_state.msgs
with st.sidebar:
    if st.button("Fechar e apagar dados"):
        import shutil
        shutil.rmtree(st.session_state.pasta, ignore_errors=True)
        st.session_state.clear()
        st.rerun()
    rotulos = sorted({r for m in msgs for r in m["rotulos"]})
    pasta_sel = st.radio("Pastas", ["Todas"] + rotulos)
    st.caption(f"{len(msgs)} mensagens")

busca = st.text_input("Buscar (assunto ou remetente)")
filtradas = [
    m for m in msgs
    if (pasta_sel == "Todas" or pasta_sel in m["rotulos"])
    and (not busca or busca.lower() in m["assunto"].lower() or busca.lower() in m["de"].lower())
]
paginas = max(1, -(-len(filtradas) // PAGE))
col_l, col_r = st.columns([2, 3])
with col_l:
    pg = st.number_input("Página", 1, paginas, 1)
    st.caption(f"{len(filtradas)} resultados")
    fatia = filtradas[(pg - 1) * PAGE: pg * PAGE]
    for i, m in enumerate(fatia):
        idx = (pg - 1) * PAGE + i
        if st.button(f"{m['de']} | {fmt(m['data'])}\n{m['assunto'][:80]}", key=f"b{idx}", use_container_width=True):
            st.session_state.sel = m
with col_r:
    m = st.session_state.get("sel")
    if m:
        msg = carregar_msg(m["arq"], m)
        st.subheader(m["assunto"])
        st.write(f"**De:** {html.escape(str(msg['from'] or ''))}")
        st.write(f"**Para:** {html.escape(str(msg['to'] or ''))}")
        st.write(f"**Data:** {fmt(m['data'])}")
        components.html(corpo_html(msg), height=600, scrolling=True)
        anexos = [a for a in msg.iter_attachments()]
        if anexos:
            st.write("Anexos:")
            for j, a in enumerate(anexos):
                st.download_button(a.get_filename() or f"anexo{j}", a.get_payload(decode=True) or b"", file_name=a.get_filename() or f"anexo{j}", key=f"a{j}")
    else:
        st.info("Selecione uma mensagem.")
