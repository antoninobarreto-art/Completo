# Roteiro de Deploy: Dojocho (Corrigido)

Este documento detalha o processo de atualização do sistema na VM do Google Cloud, mantendo a integridade do DNS, do proxy reverso, e protegendo os dados de produção.

> [!WARNING]
> **PONTOS CRÍTICOS DE ATENÇÃO DURANTE O DEPLOY:**
> 1. **Banco de Dados**: Fazer o backup do arquivo `rioaiki.db` ANTES de deletar a pasta antiga. Se não for feito, todos os dados do sistema serão apagados permanentemente.
> 2. **Segurança (JWT)**: O novo sistema exige a criação do arquivo `.env` contendo a chave `JWT_SECRET_KEY`. Sem este arquivo, o sistema não subirá e ninguém conseguirá fazer login.
> 3. **Permissões (Imagens)**: Garantir a execução do comando de permissão (`chmod -R 777 app/static`), caso contrário os usuários não conseguirão enviar fotos de perfil ou logos de dojo.

---

## 1. Parar a Versão Atual

Antes de remover o código antigo, é necessário interromper o servidor em execução:
1. Acesse a sessão do tmux:
   ```bash
   tmux attach -t dojocho
   ```
2. Interrompa o servidor (Uvicorn) pressionando **Ctrl + C**.
3. Saia/feche a sessão do tmux:
   ```bash
   exit
   ```
   *(Ou execute `pkill -f uvicorn` caso prefira encerrar o processo diretamente).*

## 2. Backup do Banco e Remover a Versão Antiga

> [!CAUTION]
> **Obrigatório:** Faça o backup do banco de dados ANTES de deletar a pasta antiga para não perder todos os cadastros!

1. Navegue até o diretório raiz:
   ```bash
   cd ~
   ```
2. **Faça o backup do banco de dados (Muito Importante)**:
   ```bash
   cp ./TesteDojocho_12AGO26/rioaiki.db ~/rioaiki_bkp_deploy.db
   ```
3. Remova a pasta do sistema anterior:
   ```bash
   rm -rf TesteDojocho_12AGO26
   ```

## 3. Subir a Nova Versão

1. **Upload:** Envie o arquivo `.zip` da nova versão (ex: `Completo-21AGO26.zip`) para a pasta `/home/antonino_barreto/`.
2. **Descompactar:**
   ```bash
   unzip Completo-21AGO26.zip -d ./Completo-21AGO26
   cd ./Completo-21AGO26
   ```
3. **Restaurar o Banco de Dados**:
   Mova o banco salvo no Passo 2 para dentro da nova pasta do sistema:
   ```bash
   cp ~/rioaiki_bkp_deploy.db ./rioaiki.db
   ```

## 4. Configurar Ambiente e Permissões

1. **Criar a Chave de Segurança (JWT) Obrigatória**:
   Crie o arquivo `.env` para que o sistema consiga gerar logins de forma segura:
   ```bash
   echo "JWT_SECRET_KEY=sua-senha-secreta-forte-aqui" > .env
   ```
2. **Criar/Ativar Ambiente Virtual**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Ajustar Permissões (Crítico)**: Para garantir que o sistema consiga salvar imagens de alunos e dojos:
   ```bash
   chmod -R 777 app/static
   ```

## 5. Iniciar o Sistema

1. Inicie uma nova sessão tmux:
   ```bash
   tmux new -s dojocho
   ```
2. Ative o ambiente e inicie o servidor na porta **8501** (Conforme configurado no Nginx):
   ```bash
   source venv/bin/activate
   python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8501
   ```
3. Desanexe da sessão (deixe rodando em background): Pressione **Ctrl + B** e depois **D**.

> [!NOTE]
> Como o DNS, Firewall e Nginx já estão configurados, o acesso via `https://dojocho.com.br` será restaurado automaticamente assim que o servidor subir.
