# Atividade Prática — Aplicação da Tríade CIA

Este projeto foi desenvolvido como parte da disciplina de Segurança da Informação. O objetivo principal é demonstrar, de forma prática e funcional, a implementação dos três pilares da Tríade CIA (**Confidencialidade, Integridade e Disponibilidade**) no desenvolvimento de software.

## 👥 Integrantes do Grupo
* Ana Beatriz
* Desiree
* Giovana Marsigli
* Isabelle
* Mariana Akemi
* Nicole

## 🛠️ Tecnologias e Bibliotecas Utilizadas
* **Linguagem:** Python 3.x
* **Bibliotecas core:**
  * `cryptography` (módulo Fernet para criptografia simétrica)
  * `hashlib` & `hmac` (para geração e verificação de hashes seguros)
  * `threading` & `shutil` (para garantir concorrência segura e automação de backups)

---

## 🏗️ Estrutura do Projeto e Mecanismos Implementados

O projeto é dividido em três módulos independentes, cada um focado em um pilar específico da segurança:

### 1. Confidencialidade (`confidencialidade.py`)
Garante que os dados sensíveis só possam ser lidos por pessoas ou sistemas autorizados.
* **Mecanismo:** Utiliza o padrão **Fernet**, que opera internamente com criptografia simétrica **AES-128 no modo CBC** combinado com um **HMAC-SHA256** para autenticação do token.
* **Funcionalidade:** O script gera automaticamente uma chave criptográfica segura (`chave_secreta.key`), cifra strings em memória e possui funções para proteger arquivos físicos completos (transformando arquivos `.txt` em arquivos cifrados `.enc`).

### 2. Integridade (`integridade.py`)
Garante que a informação não foi alterada ou corrompida, intencionalmente ou por falha, durante o armazenamento ou transmissão.
* **Mecanismo:** Implementa funções de hash **SHA-256** e códigos de autenticação de mensagem baseados em hash (**HMAC-SHA256**).
* **Funcionalidade:** Além de validar strings, o sistema gera e verifica um **manifesto de integridade em formato JSON** para conjuntos de arquivos. A validação utiliza `hmac.compare_digest()`, técnica essencial para mitigar vulnerabilidades de *timing attacks* (ataques de tempo).

### 3. Disponibilidade (`disponibilidade.py`)
Garante que o sistema e os dados permaneçam acessíveis aos usuários legítimos quando necessário.
* **Mecanismos triplos:**
  1. **Rate Limiting (Janela Deslizante):** Limita o abuso e protege o sistema contra ataques de força bruta ou negação de serviço (DoS), controlado de forma *thread-safe* com travas de concorrência (`threading.Lock`).
  2. **Retry Automático com Backoff Exponencial:** Executa tentativas de reexecução automáticas caso uma operação instável falhe, dobrando o tempo de espera a cada erro para evitar sobrecarga no servidor.
  3. **Backup Automático:** Cria cópias de segurança de arquivos críticos estruturadas com *timestamps*, permitindo a restauração imediata do estado original em caso de falha ou exclusão acidental.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
Certifique-se de ter o Python 3.x instalado em sua máquina. A biblioteca externa necessária é a `cryptography`.

### 1. Instalação das Dependências
Abra o terminal na pasta do projeto e instale a biblioteca necessária:
```bash
pip install cryptography
