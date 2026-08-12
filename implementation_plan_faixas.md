# Plano de Implementação: Correção do Critério de Aptidão a Exame (Critério 1) - [ATUALIZADO]

## 📌 Contexto & Problema
Atualmente, o **Critério 1** na rota de presença/chamada de treino ([app/routes/schedule.py](file:///c:/Users/DELL/OneDrive%20-%20Cerensa%20Tecnologia%20da%20Informa%C3%A7%C3%A3o%20S%20A/Documentos/IA/Vibe%20Coding/TesteAplicacao/app/routes/schedule.py#L216-L218)) possui um valor fixo em código (`hardcoded`) de **45 treinos** para qualquer aluno ser marcado como `ready_for_exam = True`.

Porém, a tabela de exigências por faixa no sistema já define exigências específicas de treinos acumulados para cada graduação:

| Faixa / Graduação | Treinos Mínimos Requeridos |
| :--- | :--- |
| **5º Kyu (Faixa Amarela)** | 40 treinos |
| **4º Kyu (Faixa Roxa)** | 60 treinos |
| **3º Kyu (Faixa Verde)** | 60 treinos |
| **2º Kyu (Faixa Azul)** | 90 treinos |
| **1º Kyu (Faixa Marrom)** | 100 treinos |
| **1º Dan Shodan (Faixa Preta)** | 400 treinos |
| **2º Dan Nidan / 3º Dan Sandan** | 600 treinos |
| **4º Dan Yondan ou superior** | 800 treinos |

---

## 🎯 Requisitos de Mudança

1. **Dinamização por Faixa (`belt_rank`):**
   - Na marcação de presença ([app/routes/schedule.py](file:///c:/Users/DELL/OneDrive%20-%20Cerensa%20Tecnologia%20da%20Informa%C3%A7%C3%A3o%20S%20A/Documentos/IA/Vibe%20Coding/TesteAplicacao/app/routes/schedule.py)), substituir o valor fixo de 45 pela função utilitária centralizada que obtém os treinos requeridos de acordo com a faixa atual do aluno.
2. **Consistência de Cálculo (Centralização em Utilitário Comum):**
   - Mover a função `get_req_attendances_filter` para um arquivo utilitário comum (`app/utils.py`) para ser consumida tanto pelo `dashboard.py` (renderização Jinja2) quanto pelo `schedule.py` (gravação da chamada) e `management.py` (edição de aluno).

---

## 🛠️ Alterações Propostas

### 1. Criar Módulo Utilitário (`app/utils.py`)
- Definir e exportar a função `get_required_attendances(belt_rank: str) -> int`:
  ```python
  def get_required_attendances(belt_rank: str) -> int:
      if not belt_rank:
          return 60
      r_c = belt_rank.lower()
      if "5º" in r_c or "5 kyu" in r_c or "amarela" in r_c:
          return 40
      elif "4º" in r_c or "4 kyu" in r_c or "roxa" in r_c:
          return 60
      elif "3º" in r_c or "3 kyu" in r_c or "verde" in r_c:
          return 60
      elif "2º" in r_c or "2 kyu" in r_c or "azul" in r_c:
          return 90
      elif "1º" in r_c or "1 kyu" in r_c or "marrom" in r_c or "castanha" in r_c:
          return 100
      elif "shodan" in r_c or "1º dan" in r_c or "1 dan" in r_c:
          return 400
      elif "nidan" in r_c or "2º dan" in r_c or "2 dan" in r_c:
          return 600
      elif "sandan" in r_c or "3º dan" in r_c or "3 dan" in r_c:
          return 600
      elif "yondan" in r_c or "4º dan" in r_c or "4 dan" in r_c or "godan" in r_c or "5º dan" in r_c or "rokudan" in r_c:
          return 800
      return 60
  ```

### 2. Atualizar Chamada de Treino ([app/routes/schedule.py](file:///c:/Users/DELL/OneDrive%20-%20Cerensa%20Tecnologia%20da%20Informa%C3%A7%C3%A3o%20S%20A/Documentos/IA/Vibe%20Coding/TesteAplicacao/app/routes/schedule.py))
- Ao incrementar `st.total_attendances += 1`, comparar diretamente com `get_required_attendances(st.belt_rank)`:
  ```python
  st.total_attendances += 1
  req_att = get_required_attendances(st.belt_rank)
  if st.total_attendances >= req_att:
      st.ready_for_exam = True
  ```

### 3. Importar e Registrar Utilitário no Dashboard ([app/routes/dashboard.py](file:///c:/Users/DELL/OneDrive%20-%20Cerensa%20Tecnologia%20da%20Informa%C3%A7%C3%A3o%20S%20A/Documentos/IA/Vibe%20Coding/TesteAplicacao/app/routes/dashboard.py))
- Usar `get_required_attendances` importado de `app.utils` para alimentar os filtros do Jinja2 e evitar código duplicado.

### 4. Atualizar Edição Manual na Gestão ([app/routes/management.py](file:///c:/Users/DELL/OneDrive%20-%20Cerensa%20Tecnologia%20da%20Informa%C3%A7%C3%A3o%20S%20A/Documentos/IA/Vibe%20Coding/TesteAplicacao/app/routes/management.py))
- Ao salvar alterações no total de treinos do aluno, atualizar automaticamente `st.ready_for_exam = True` caso o novo total atinja ou supere o requisito da faixa do aluno.

---

## 🧪 Plano de Verificação

### Automated / Diagnostic Verification
- Testar a gravação de presença para alunos de diferentes faixas.
- Confirmar se o servidor FastAPI recarrega limpo sem nenhum erro.
