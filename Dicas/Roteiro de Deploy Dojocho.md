Roteiro de Deploy: Dojocho

Este documento detalha o processo de atualização do sistema na VM do Google Cloud, 
mantendo a integridade do DNS e do proxy reverso.

1. Parar a Versão Atual
Antes de remover o código antigo, é necessário interromper o servidor em execução:
Acesse a sessão do tmux:
tmux attach -t dojocho
Interrompa o servidor (Uvicorn) pressionando Ctrl + C.
Saia/feche a sessão do tmux:
exit(Ou execute pkill -f uvicorn caso prefira encerrar o processo diretamente).

2. Remover a Versão Antiga
Limpe o diretório de trabalho para evitar conflitos:
Navegue até o diretório raiz:
cd ~
Remova a pasta do sistema anterior:
rm -rf TesteDojocho_12AGO26

3. Subir a Nova Versão
Upload: Envie o arquivo Completo-19AGO26.zip para a pasta /home/antonino_barreto/.
Descompactar:
unzip Completo-19AGO26.zip -d ./Completo-19AGO26
cd ./Completo-19AGO26

4. Configurar Ambiente e Permissões
Criar/Ativar Ambiente Virtual:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Ajustar Permissões (Crítico): Para garantir que o sistema consiga salvar imagens de alunos e dojos:
chmod -R 777 app/static

5. Iniciar o Sistema
Inicie uma nova sessão tmux:
tmux new -s dojocho
Ative o ambiente e inicie o servidor:
source venv/bin/activate
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8501

Desanexe da sessão (deixe rodando em background): Pressione Ctrl + B e depois D.

Nota: Como o DNS, Firewall e Nginx já estão configurados, o acesso via https://dojocho.com.br 
será restaurado automaticamente assim que o servidor subir.
