# 🏡 Verificador & Comparador de Aluguel de Casas, Chácaras e Sítios

> Aplicação web moderna para busca centralizada e comparação de preços de aluguéis de temporada (chácaras, sítios e casas de campo/praia) entre múltiplos portais (**TemporadaLivre**, **OLX**, e expansível para **Airbnb** e **Booking**).

Projetada seguindo as melhores práticas de desenvolvimento, com consumo otimizado de recursos para execução no seu **Homelab via Portainer** e hospedagem de código no **GitHub**.

---

## 🚀 Funcionalidades

- **Comparação Real de Valores**: Calcula o custo total da estadia (diárias $\times$ noites $+$ taxa de limpeza $+$ taxa de plataforma) e indica qual portal oferece o menor preço.
- **Filtros Avançados**:
  - Região / Cidade (ex: Atibaia, Ibiúna, Ubatuba, Brotas)
  - Datas de entrada (check-in) e saída (check-out)
  - Quantidade de hóspedes
  - Faixa de preço mínimo e máximo
  - Comodidades obrigatórias: Piscina, Churrasqueira, Pet-friendly
  - Tipo de propriedade: Chácara, Sítio ou Casa
- **Scraping Modular**: Arquitetura desacoplada via `BaseScraper`, facilitando a adição de novos portais.
- **Cache de Alta Performance**: Armazenamento temporário de cotações em **Redis** para evitar requisições repetidas e garantir resposta instantânea.
- **Pronto para Homelab**: Containers Docker com limites de CPU/RAM configurados para rodar 24/7 sem sobrecarregar seu servidor.

---

## 🏗️ Arquitetura

- **Frontend**: React 18, Vite, TailwindCSS, Lucide Icons, Nginx Alpine.
- **Backend API**: Python 3.11+, FastAPI assíncrono, Pydantic v2, SQLAlchemy 2.0.
- **Banco de Dados**: PostgreSQL 16 (com suporte a SQLite local).
- **Cache & Mensageria**: Redis 7 Alpine.
- **Orquestração**: Docker Compose.

---

## 🐳 Como Subir no Portainer (Homelab)

### Passo 1: Criar a Stack no Portainer
1. Acesse o painel do seu **Portainer**.
2. Vá no menu lateral em **Stacks** e clique em **+ Add stack**.
3. Defina o nome da Stack (ex: `aluguel-temporada`).
4. Escolha o método de build **Repository**:
   - **Repository URL**: `https://github.com/edu-ricardo/verificador-aluguel.git`
   - **Repository reference**: `refs/heads/main`
   - **Compose path**: `docker-compose.yml`
   - Ative a opção **Automatic updates** (Webhook ou Polling) se desejar que o Portainer atualize os containers automaticamente a cada `git push`.

### Passo 2: Configurar as Variáveis de Ambiente
Na seção **Environment variables** do Portainer, preencha as variáveis baseadas no `.env.example`:

```env
POSTGRES_USER=verificador
POSTGRES_PASSWORD=defina_uma_senha_forte_aqui
POSTGRES_DB=aluguel_temporada
BACKEND_PORT=8025
FRONTEND_PORT=5025
ENVIRONMENT=production
```

### Passo 3: Deploy da Stack
- Clique em **Deploy the stack**. O Portainer fará o clone do repositório, compilará as imagens e subirá os 4 serviços (`aluguel_frontend`, `aluguel_backend`, `aluguel_postgres`, `aluguel_redis`).
- Acesse a interface web em `http://IP_DO_SEU_HOMELAB:5025`.
- Acesse a documentação Swagger da API em `http://IP_DO_SEU_HOMELAB:8025/docs`.

---

## 💻 Executando Localmente com Docker Compose

Caso queira rodar diretamente na sua máquina de desenvolvimento com Docker:

```bash
# 1. Clone o repositório
git clone https://github.com/edu-ricardo/verificador-aluguel.git
cd verificador-aluguel

# 2. Copie o arquivo de variáveis de ambiente
cp .env.example .env

# 3. Suba os containers
docker compose up -d --build

# 4. Acompanhe os logs
docker compose logs -f
```

---

## 🛠️ Executando Manualmente em Modo Desenvolvimento

### Backend (FastAPI):
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8025
```

### Frontend (React):
```bash
cd frontend
npm install
npm run dev
```

---

## 🧩 Adicionando Novos Scrapers de Portais

Para plugar um novo portal (ex: Airbnb, Booking ou Vrbo), basta criar uma nova classe herdando de `BaseScraper` em `backend/app/scrapers/`:

```python
from app.scrapers.base import BaseScraper, ScrapedProperty

class NovoPortalScraper(BaseScraper):
    platform_name = "Novo Portal"
    platform_code = "novoportal"

    async def search(self, city, state, check_in, check_out, guests, property_type):
        # 1. Requisite a página ou API do portal
        # 2. Extraia diária, fotos e comodidades
        # 3. Retorne lista de ScrapedProperty normalizada
        return []
```
E registre o novo scraper na lista `self.scrapers` dentro de `backend/app/services/search_service.py`.

---

## 🧪 Testes Automatizados

```bash
cd backend
pytest -v
```

---

## 📄 Licença

Distribuído sob a licença MIT. Consulte `LICENSE` para mais detalhes.
