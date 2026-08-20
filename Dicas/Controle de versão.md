A Importância da Organização no "Vibe Coding" [00:43]:
https://youtu.be/Hhey8XwowEA

Quando um SaaS entra em produção e passa a ter usuários ativos, fazer alterações diretas na branch main ou confiar apenas no histórico de chats com IA 
gera perda de rastreabilidade e retrabalho [01:23].

A solução é adotar uma esteira de trabalho baseada em pequenas evoluções controladas, unindo ramificações de Git com especificações formais [02:44].

Git Flow Simplificado na Prática [02:58]:

Branch main: Representa o ambiente de produção; qualquer commit/merge dispara a publicação automática via plataformas como Render [03:06].

Feature Branches: Criação de branches específicas a partir da main (ex.: feature/adicionar-pino-mapa) para isolar o desenvolvimento [12:28].

Pull Request e Merge: Após os testes e a conclusão da demanda, abre-se um Pull Request para a main, acionando o deploy apenas quando o código estiver validado [16:19].

Metodologia com OpenSpec (Spec-Driven Development - SDD) [06:13]:

Instalação e Setup: Adição do OpenSpec via terminal (npm install) e inclusão da pasta .opencode no .gitignore (mantendo a pasta openspec versionada para histórico documental) [11:57].

Fluxo em 3 Etapas:

Explore (/opsx-explorer): Conversa exploratória para mapear regras de negócio e requisitos sem alterar arquivos [13:05].

Propose / Apply (/opsx-apply): Geração da proposta estruturada e aplicação do código correspondente [14:15].

Archive (/opsx-archive): Sincronização e arquivamento das decisões tomadas para criar uma base de conhecimento versionada no projeto [15:24].

Recuperação de Fluxo com Git Stash [20:26]:

Demonstração de cenário comum em que o desenvolvedor esquece de criar a nova branch antes de iniciar outra alteração [17:04].

Passo a passo de correção: Salvar alterações locais com git stash (incluindo untracked), atualizar a main, criar a nova branch da feature e aplicar as modificações salvas via stash pop [20:58].

Consumo e Comparativo de Modelos de IA [08:25]:

Grok 4.5: Alto consumo de cota operacional (gastou quase 25% do limite de 5 horas em apenas 10 minutos de inicialização e bateu mais de 90% em duas alterações simples) [09:16].

DeepSeek: Alternativa econômica com entrega técnica equivalente [17:58].

Conclusão de Custos: Quando a IA é guiada por um contexto bem delimitado e especificações claras (como no framework "Pegada de Silício" e OpenSpec), a diferença de qualidade entre modelos topo de linha e modelos mais acessíveis torna-se mínima, não justificando o gasto excessivo de saldo [18:27].