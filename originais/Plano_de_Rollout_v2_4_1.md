# Plano de Rollout para Ambiente de Produção com Dados Reais (v2.4.0)

Este documento descreve o plano detalhado e o passo a passo seguro para publicar o sistema **DOJOCHO (v2.4.0)** em ambiente de produção com dados reais dos Dojos e Alunos.

---

## User Review Required

> [!IMPORTANT]
> **Definição das Credenciais Iniciais**: No ambiente de produção, todos os usuários importados precisarão receber uma senha inicial ou utilizar o fluxo de recuperação de senha ("Esqueci minha senha").
> 
> **Decisão recomendada**: Definir uma senha padrão temporária para o primeiro acesso e forçar a troca no primeiro login, ou disponibilizar a chave `JWT_SECRET_KEY` forte para produção.

> [!WARNING]
> **Limpeza de Dados Fictícios**: O banco de dados atual possui registros fictícios de treinos e presenças que foram criados para homologação gráfica. Antes de ir para produção, a tabela de presenças e sessões de treino fictícias deve ser zerada para a entrada dos dados reais.

---

## Open Questions

> [!IMPORTANT]
> 1. ~~**Qual a infraestrutura de hospedagem escolhida?**~~ Respondido: O servidor web já está funcional em `dojocho.com.br`.
> 2. ~~**Os dados da planilha `Alunos Dojoweb.xlsx` já são a versão final e oficial** para a carga de produção?~~ Respondido: Sim, o arquivo `C:\DOJOCHO\Completo\originais\Alunos Dojoweb.xlsx` é a versão oficial. O usuário verificará se há outras planilhas com dados complementares.

---

## Passo a Passo do Rollout

---

### Fase 1: Preparação e Higienização do Banco de Dados Real

### Fase 1: Preparação e Higienização do Banco de Dados Real

1. **Backup Seguro da Versão Atual**:
   - Mova ou copie o arquivo `rioaiki.db` atual para fora do diretório da aplicação antes de qualquer deleção (ex: `cp ./PastaDoSistema/rioaiki.db ~/rioaiki_bkp.db`).
2. **Purga de Dados Fictícios de Teste**:
   - Zerar tabelas de teste: `attendances` (presenças fictícias) e `class_sessions` (aulas fictícias).
   - Manter as estruturas de Dojos, Horários de Aulas (`class_schedules`), Usuários e Relacionamentos confirmados.
3. **Carga dos Dados Reais**:
   - Re-executar a carga oficial da planilha de alunos com status estrito de `Ativo` / `Inativo` e vínculo correto aos Dojos.
   - Garantir a associação do Sensei responsável (ex: Fábio Castro e demais professores).

---

### Fase 2: Configuração de Segurança e Ambiente de Produção

1. **Configuração de Variáveis de Ambiente (`.env`)**:
   - Criar o arquivo `.env` na raiz do NOVO diretório de produção com as variáveis críticas:
     ```env
     JWT_SECRET_KEY=<chave-secreta-forte-e-aleatoria-de-64-caracteres>
     ENVIRONMENT=production
     PORT=8501
     ```
2. **Segurança de Senhas e Acesso**:
   - Garantir que a senha do usuário `ADMIN` seja alterada para uma senha forte exclusiva.
   - Configurar o parâmetro de cookie seguro (HTTPS flag) na autenticação JWT.

---

### Fase 3: Infraestrutura e Servidor WEB (Reverse Proxy + HTTPS)

1. **Configuração do Servidor ASGI**:
   - Em vez do `--reload`, rodar Uvicorn de forma persistente (ex: usando tmux e ativando o venv):
     ```bash
     python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8501
     ```
2. ~~**Proxy Reverso com SSL/HTTPS**~~: *(Já Concluído - DNS, Firewall e Nginx configurados)*
   - O acesso via `https://dojocho.com.br` será restaurado automaticamente assim que o servidor Uvicorn subir na porta `8501`.
3. **Rotina de Backup Automático do Banco (SQLite)**:
   - Configurar uma rotina diária (Cron job / Task Scheduler) para realizar snapshot do arquivo `rioaiki.db` com retenção de 30 dias.

---

### Fase 4: Go-Live (Lançamento Oficial) e Onboarding

1. **Checagem Pré-Lançamento (Smoke Test)**:
   - Teste de login de Admin, Sensei e Aluno.
   - Teste de chamada de presença em aula.
   - Validação da renderização dos gráficos com base real zerada.
2. **Comunicação aos Usuários**:
   - Envio das instruções de acesso e credenciais temporárias para os alunos e Senseis.

---

## Verification Plan

### Automated Tests
- Executar os testes automatizados da aplicação antes do deploy:
  ```bash
  pytest tests/
  ```

### Manual Verification
1. **Verificação de SSL/HTTPS**: Acessar o domínio de produção e verificar se o certificado SSL está válido e seguro.
2. **Teste de Login e Permissões**: Logar como Sensei e validar se apenas os Dojos sob sua responsabilidade podem ser editados.
3. **Teste de Chamada Real**: Cadastrar uma aula e registrar presenças reais.
4. **Verificação de Integridade do Banco**: Confirmar que a versão `PRAGMA user_version` está igual a `2.4.0`.
