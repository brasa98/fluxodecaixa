# Caminhos
EDITOR = nvim
VER = glow
SPRINT_DIR = sprint

# Sprint: abrir log de progresso
log:
	$(EDITOR) $(SPRINT_DIR)/log.md

# Sprint: iniciar uma nova seção do diário (com data)
novoLog:
	echo "## $(shell date '+%Y-%m-%d')" >> $(SPRINT_DIR)/log.md && \
	echo "" >> $(SPRINT_DIR)/log.md && \
	$(EDITOR) + $(SPRINT_DIR)/log.md

# Rodar script de setup
setup:
	bash setup.sh

# Limpar os .pyc (compilados)
limpar:
	find . -name "*.pyc" -delete
	rm -rf __pycache__

# Instalar dependências do projeto
instalar:
	pip install -r requirements.txt

verTODOS:
	@cat README.md | grep -E '^\s*-\s\[\s\]'

# === Etapas do Sprint ===

# Dia 1 - Entender
dia1:
	@task description:SpDia1 start
	$(EDITOR) $(SPRINT_DIR)/D1-Entender.md
	@task description:SpDia1 done

vdia1:
	$(VER) $(SPRINT_DIR)/D1-Entender.md

# Dia 2 - Esboçar
dia2:
	@task description:SpDia2 start
	$(EDITOR) $(SPRINT_DIR)/D2-Esboçar.md
	@task description:SpDia2 done

vdia2:
	$(VER) $(SPRINT_DIR)/D2-Esboçar.md

# Dia 3 - Decidir
dia3:
	@task description:SpDia3 start
	$(EDITOR) $(SPRINT_DIR)/D3-Decisão.md
	@task description:SpDia3 done

vdia3:
	$(VER) $(SPRINT_DIR)/D3-Decisão.md

# Dia 4 - Prototipar
dia4:
	@@task description:SpDia4 start
	$(EDITOR) $(SPRINT_DIR)/D4-Prototipar.md
	@task description:SpDia4 done

vdia4:
	$(VER) $(SPRINT_DIR)/D4-Prototipar.md

# Dia 5 - Testar
dia5:
	@task description:SpDia5 start
	$(EDITOR) $(SPRINT_DIR)/D5-Testar.md
	@task description:SpDia5 done

vdia5:
	$(VER) $(SPRINT_DIR)/D5-Testar.md


# Ver status do sprint
status:
	@echo "📌 Status do Sprint Garracio:"
	@task project:Garracio sort:due
	@task project:Garracio summary


# Limpa completamente todas as tarefas do projeto Garracio
limparSprint:
	@echo "🧼 Limpando completamente o projeto Garracio do Taskwarrior..."

	@task project:Garracio status:pending rc.confirmation=no delete || true
	@task project:Garracio status:completed rc.confirmation=no delete || true
	@task project:Garracio status:waiting rc.confirmation=no delete || true
	@task project:Garracio status:recurring rc.confirmation=no delete || true
	@task project:Garracio status:deleted rc.confirmation=no purge || true

	@echo "✅ Tarefas do projeto Garracio completamente removidas."


# Recomeçar semana
resetarSprint:
	@echo "🔄 Salvando e resetando arquivos do Sprint..."

	@mkdir -p $(SPRINT_DIR)/semanas

	@numSemana=$$(ls -1 $(SPRINT_DIR)/semanas | grep -E '^semana[0-9]+:' | wc -l); \
	numSemanaDir=$$((numSemana + 1)); \
	read -p "📝 Dê um título à semana $$numSemanaDir: " TITULO; \
	novaPasta="$(SPRINT_DIR)/semanas/semana$$numSemanaDir: $$TITULO"; \
	mkdir -p "$$novaPasta"; \
	mv $(SPRINT_DIR)/D*-*.md "$$novaPasta" 2>/dev/null || true; \
	mkdir -p "$$novaPasta/testes"; \
	find $(SPRINT_DIR) -maxdepth 1 -type f ! -name 'D*-*.md' -exec mv {} "$$novaPasta/testes/" \; 2>/dev/null || true; \
	echo "🗃️ Sprint atual salvo em $$novaPasta"

	@echo "📃 Recriando templates..."

	@echo -e "# 🗺️ Dia 1 – Entender\n\n## 🎯 Objetivo\n> Defina claramente o problema que você quer resolver.\n- Faça uma história de usuário.\n\n## 📖 Contexto\n> Qual o histórico, usuários e contexto do problema?\n\n## ⛳️ Objetivo de Longo Prazo\n> Qual o objetivo de longo prazo?\n- ...\n\n## ❓️ Perguntas principais\n- O que pode dar errado?\n- Quais as incertezas?\n\n## 📝 Notas e insights\n- ..." > $(SPRINT_DIR)/D1-Entender.md

	@echo -e "# 📝 Dia 2 – Esboçar\n\n## 💭 Inspiração\n> Soluções existentes ou ideias similares?\n\n## 📄 Rascunhos / Ideias\n- 💡 Ideia 1:\n- 💡 Ideia 2:\n- 💡 Ideia 3:\n\n## 🎖️ Solução preferida\n> Descreva a ideia mais promissora.\n...\n\n### ❓️ Por quê\n- ..." > $(SPRINT_DIR)/D2-Esboçar.md

	@echo -e "# 🤔 Dia 3 – Decidir\n\n## 💭 Ideias comparadas\n### 💡 Ideia A\n\t\n- ...\n### 💡 Ideia B\n\t\n- ...\n## 🎖️ Solução escolhida\n> Detalhe a solução final.\n\n## ➡️ Fluxo simplificado\n> Passos ou fluxograma básico da ideia." > $(SPRINT_DIR)/D3-Decisão.md

	@echo -e "# 🤖 Dia 4 – Prototipar\n\n## 📝 Plano do protótipo\n- 🖥️ O que será demonstrado?\n- 🛠️ Que ferramentas usará?\n- ⌨️ Desenvolvimento do protótipo\n> Use o Fluxo criado no Dia 3.\n\n## ✅ Tarefas\n- [ ] Tarefa 1\n- [ ] Tarefa 2\n- [ ] Tarefa 3" > $(SPRINT_DIR)/D4-Prototipar.md

	@echo -e "# ⚙️ Dia 5 – Testar\n\n## 🤖 Implementação e Desenvolvimento\n> Relate como foi a implementação e destaque mudanças feitas no protótipo.\n\n## 📑 Método de teste\n> Teste manual, reflexão, simulação?\n\n## 💬 Feedback / Aprendizados\n- ..." > $(SPRINT_DIR)/D5-Testar.md

	@echo "🧹 Limpando tarefas do Taskwarrior..."
	@task project:Garracio status:pending rc.confirmation=no delete || true

	@echo "➕ Criando tarefas do Sprint no Taskwarrior..."
	@task add SpDia1 project:Garracio due:Tuesday
	@task add SpDia2 project:Garracio due:Wednesday
	@task add SpDia3 project:Garracio due:Thursday
	@task add SpDia4 project:Garracio due:Friday
	@task add SpDia5 project:Garracio due:Saturday

	@echo "✅ Sprint reiniciado com sucesso!"


versaoNova:
	@read -p "📝 Nomeie a versão: " nomeVersao; \
	if git status | grep -q "not staged"; then \
		echo "❎ Tem mudanças não salvas para o commit."; \
	else \
		nv README.md; \
		echo "⚙️ Fazendo commit e criando branch 'v$${nomeVersao}'..."; \
		git checkout dev; \
		git commit -m "v$${nomeVersao}"; \
		git checkout -b "v$${nomeVersao}"; \
		git commit --allow-empty -m "init v$${nomeVersao}"; \
		git push origin "v$${nomeVersao}"; \
	fi

pushDev:
	@read -p "📝 Nomeie o commit: " mensagem; \
	git checkout dev; \
	git commit -m "$${mensagem}"; \
	git push origin dev

criarRelease:
	@bash -c '\
	read -p "📝 Nome da versão: " nomeVersao; \
	read -p "🖥️ Plataforma: " plataforma; \
	if [ "$$plataforma" = "linux" ]; then \
		pyinstaller --onefile --clean --name "garracio" --add-data="garracio.json:." --add-data="templates:templates" --add-data="static:static" main.py; \
		zip "Garracio-v$$nomeVersao-$$plataforma.zip" dist/garracio setup.sh; \
	else \
		pyinstaller --onefile --clean --name "garracio.exe" --add-data="garracio.json:." --add-data="templates:templates" --add-data="static:static" main.py; \
		zip "Garracio-v$$nomeVersao-$$plataforma.zip" dist/garracio.exe setup.bat; \
	fi'

REPO := olucasfracaro/Garracio
WORKFLOW := build.yml
BRANCH := dev

buildRelease:
	@if [ -z "$(description)" ]; then \
		echo "❌ Você deve fornecer a descrição da release: make buildRelease description=\"vX.Y.Z\""; \
		exit 1; \
	fi
	@echo "🚀 Disparando workflow '$(WORKFLOW)' na branch '$(BRANCH)' com descrição: '$(description)'..."
	@gh workflow run $(WORKFLOW) --repo $(REPO) --ref $(BRANCH) --field description="$(description)"

buildStatus:
	@echo "🔍 Verificando status do último workflow dispatch na branch '$(BRANCH)'..."
	@gh run list --repo $(REPO) --branch $(BRANCH) --limit 1

baixarArtefatos:
	@echo "📦 Baixando artefatos da última execução da branch '$(BRANCH)'..."
	@LAST_RUN_ID=$$(gh run list --repo $(REPO) --branch $(BRANCH) --limit 1 --json databaseId -q '.[0].databaseId'); \
	if [ -z "$$LAST_RUN_ID" ]; then \
		echo "❌ Nenhuma run encontrada."; \
		exit 1; \
	fi; \
	gh run download $$LAST_RUN_ID --repo $(REPO) --dir artRelease
	@echo "✅ Artefatos salvos na pasta ./artRelease"
