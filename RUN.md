# Rotina diária: 3 curtos do Além do Fato (dossiê 9:16) agendados no Buffer

Siga a skill **video-dossie-alem-do-fato** para todas as regras de conteúdo, checagem e estilo. Este arquivo descreve só a parte automática. Trabalhe sem pedir autorização no meio do caminho e gaste poucos tokens.

## 0. Ambiente
```bash
git clone --depth 1 https://github.com/alemdofatottk-ship-it/alemdofato-videos /home/claude/alemdofato-videos
cd /home/claude/alemdofato-videos && ./setup.sh
mkdir -p ~/.af && chmod 700 ~/.af   # grave BUFFER_KEY e GEMINI_KEY (vindos do prompt da tarefa) em ~/.af/keys.env
set -a; . ~/.af/keys.env; set +a
```

## 1. Escolher 3 temas
- Pesquisar na web os assuntos mais quentes das últimas 24–48 h em notícias do Brasil e do mundo, histórias curiosas e investimentos.
- Não repetir nada de `historico.json` (lista de temas já postados).
- Variar: idealmente 1 notícia, 1 história do mundo e 1 de economia/investimentos.
- Checar todos os fatos em pelo menos 2 fontes confiáveis. Em casos policiais, atribuir a acusação e incluir "a defesa nega". Em investimentos, incluir "Isso não é recomendação de investimento".

## 2. Para cada tema: pasta `dias/AAAA-MM-DD/N/` com
- `roteiro.txt`: 180–200 palavras, frases curtas, números por extenso, gancho forte, pergunta de comentário com opções e "o próximo caso vai ser postado aqui no perfil", e termina com "Siga o Além do Fato." (um único "siga").
- `titulo.txt`: título falado pela voz grátis (escrita fonética se preciso).
- `python3 lib/pipeline.py voice DIR` (Gemini flash TTS; se der 429 em todos os modelos, use os vídeos que deram certo e avise no resumo).
- `spec.py`: copie o formato de `exemplos/faa/spec.py`. Batidas de 1,5 a 4 s, maioria animação (`sp`, `map`, `dos`, `type`), `txt` só para gancho e frases de impacto, sem repetir o mesmo tipo mais de 2 vezes seguidas, `poll` na pergunta e `follow` no "Siga".
  - Cenas prontas em `lib/scenes.py`: clock, grounded, network, cables, board, chart, court, newspaper, money. Se o tema pedir, crie uma cena nova no mesmo estilo (noir, sem sol vermelho, sem pessoas reais, sem personagens protegidos) e faça commit.
  - Personagens (`person`) em quase toda cena `sp`, do lado direito.
  - Mapa (`map`) sempre que citar um lugar.
- `python3 lib/pipeline.py render DIR` e abrir `folha.jpg` para conferir (nada cortado, nada sobreposto, nenhuma tela parada).
- `meta.json`:
```json
{"title": "...", "desc": "mini descrição (2-3 frases + pergunta)",
 "tags_social": ["#alemdofato", "#...", "#...", "#...", "#..."],
 "tags_yt": ["#alemdofato", "#shorts", "... total 10"],
 "due_at": "AAAA-MM-DDTHH:MM:00Z"}
```
Horários (dia seguinte, Brasília): 12:00, 18:00 e 21:00 → UTC 15:00, 21:00 e 00:00 (do dia depois). Postar primeiro o assunto que envelhece mais rápido.

## 3. Pedir aprovação (obrigatório)
O usuário quer aprovar antes de cada agendamento. Envie os 3 vídeos e as 3 capas (SendUserFile) com título, horário e fontes de cada um, e pergunte (AskUserQuestion) quais pode agendar. **Só publique os aprovados.** Se ninguém responder, não agende nada; diga no resumo que os vídeos ficaram prontos esperando aprovação.

## 4. Publicar (só após o "sim")
```bash
python3 lib/pipeline.py publish dias/AAAA-MM-DD/1 dias/AAAA-MM-DD/2 dias/AAAA-MM-DD/3
```
Sobe os MP4 no branch `media` (commit órfão, só os vídeos ainda não publicados) e agenda nos 3 canais via Buffer. Confira em `agendado.json` que os 3 canais voltaram com `post.id`.

## 5. Fechar
- Acrescentar os 3 temas em `historico.json`; commit e push no `main` (sem MP4, sem chaves).
- Mandar ao usuário (SendUserMessage) um resumo curto: os 3 títulos, horários, e as fontes de cada um. Enviar as 3 capas com SendUserFile.
- Se algo falhar, dizer exatamente o que falhou e o que ficou agendado.
