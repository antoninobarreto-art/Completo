# ☁️ Guia de Implantação do DOJOCHO na VM do Google Cloud Platform (GCP)

Este guia documenta o passo a passo para implantar o sistema **DOJOCHO** em uma Máquina Virtual (Compute Engine) no Google Cloud, garantindo acesso por navegadores web em computadores e celulares.

---

## 1. Requisitos da VM no GCP
- **Sistema Operacional**: Ubuntu 22.04 LTS ou Ubuntu 24.04 LTS.
- **Tipo de Instância**: `e2-micro` (nível gratuito do GCP) ou `e2-small` (recomendado para uso de múltiplos dojos).
- **Rede / Firewall**: Liberar portas de entrada HTTP (`80`), HTTPS (`443`) e `8000`.

---

## 2. Passo a Passo de Instalação na VM

### A. Atualizar o sistema e instalar dependências
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx
```

### B. Clonar o Repositório e Configurar Ambiente
```bash
sudo mkdir -p /opt/dojocho
sudo chown -R $USER:$USER /opt/dojocho
cd /opt/dojocho
# Clocar repositório ou copiar pasta do projeto
cd Completo

python3 -m venv venv
source venv/bin/venv/activate  # Ou venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3. Configuração do Serviço da Aplicação (`systemd`)

Copie o arquivo de serviço para o diretório de serviços do sistema Linux:

```bash
sudo cp /opt/dojocho/Completo/scripts/dojocho.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable dojocho
sudo systemctl start dojocho
sudo systemctl status dojocho
```

---

## 4. Configuração de Nginx como Proxy Reverso com HTTPS (Certbot)

Criar o arquivo `/etc/nginx/sites-available/dojocho`:

```nginx
server {
    server_name dojocho.seudominio.com.br; # Ou o IP da VM

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Ativar site e obter certificado SSL gratuito:

```bash
sudo ln -s /etc/nginx/sites-available/dojocho /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo certbot --nginx -d dojocho.seudominio.com.br
```

---

## 5. Regras de Firewall no Google Cloud Shell / Console
Garantir que as seguintes portas estão liberadas no GCP Compute Engine:
```bash
gcloud compute firewall-rules create allow-http-https-dojocho \
    --allow tcp:80,tcp:443,tcp:8000 \
    --target-tags=http-server,https-server
```
