# Leitor de E-mails do Google Takeout

Aplicativo simples para **visualizar e-mails exportados do Gmail pelo Google Takeout**, com aparência de um programa de e-mail. Ele só lê: não envia, não edita e não apaga nada.

## Para quem é

Para qualquer pessoa, sem conhecimento técnico. Você abre a página, escolhe o arquivo e lê.

## Como usar (versão online)

1. Abra o link: **https://SEU-USUARIO.github.io/NOME-DO-REPOSITORIO/**
2. Aguarde o carregamento (na primeira vez pode levar até 1 minuto).
3. Clique em **Importar arquivo** e escolha o arquivo `.mbox` (ou o `.zip` / `.tgz` do Takeout).
4. Clique em **Importar**.
5. Navegue: pastas à esquerda, lista de mensagens no meio e leitura à direita.
6. Ao terminar, clique em **Fechar e apagar dados** ou feche a aba.

## Seus dados estão seguros?

- O app roda **dentro do seu navegador**. O arquivo não é enviado a nenhum servidor.
- O GitHub só entrega a página; ele não recebe os seus e-mails.
- Ao fechar a aba, os dados desaparecem da memória.
- Imagens remotas e scripts dentro dos e-mails são bloqueados.
- Atenção: o carregamento inicial exige internet para baixar o motor do app. Depois de carregado, a leitura do arquivo é feita localmente.

## Como obter o arquivo do Google Takeout

1. Acesse https://takeout.google.com
2. Clique em "Desmarcar tudo" e marque apenas **Gmail**.
3. Escolha o formato de arquivo (.zip) e clique em **Criar exportação**.
4. Quando o Google avisar por e-mail, baixe o arquivo.
5. Use esse arquivo (ou o `.mbox` de dentro dele) no app.

## Limitações

- Arquivos muito grandes (acima de 1 a 2 GB) podem travar o navegador, pois a versão online usa a memória do navegador. Para esses casos, use a versão local (abaixo) ou separe a exportação em partes menores.
- Imagens embutidas no corpo do e-mail podem aparecer quebradas.
- Use um navegador atualizado (Chrome, Edge ou Firefox) em computador.

## Para quem quiser rodar localmente (opcional)

```bash
pip install streamlit
streamlit run app.py
```

Abra http://127.0.0.1:8501. O arquivo `.streamlit/config.toml` já restringe o servidor ao seu computador.

## Para quem publica no GitHub Pages

O GitHub Pages só serve páginas estáticas e não executa Python. Por isso usamos o **stlite**, que roda o Streamlit dentro do navegador.

1. Instale: `pip install stlitepack`
2. Gere a página (cria `docs/index.html`):
   ```python
   from stlitepack import pack
   pack("app.py")
   ```
3. Envie o repositório ao GitHub.
4. Em **Settings > Pages**, escolha *Deploy from a branch*, a branch `main` e a pasta `/docs`.
5. Após alguns minutos, o link aparece na mesma tela.

Sempre que alterar o `app.py`, rode o `pack` de novo e envie as mudanças.

## Estrutura

```
app.py                  # aplicativo
requirements.txt        # dependências
.streamlit/config.toml  # configuração local
docs/index.html         # versão para GitHub Pages (gerada)
```
