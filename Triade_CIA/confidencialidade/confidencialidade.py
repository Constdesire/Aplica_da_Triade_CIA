import os
import sys
import io
import subprocess
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

try:
    from cryptography.fernet import Fernet
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography", "-q"])
    from cryptography.fernet import Fernet

def separador(titulo: str):
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print('='*60)

class GerenciadorConfidencialidade:
    def __init__(self, arquivo_chave: str = "chave_secreta.key"):
        # A chave de criptografia nunca deve ficar hardcoded (fixa) no código-fonte.
        # Por isso, gerenciamos a chave em um arquivo externo separado.
        self.arquivo_chave = arquivo_chave
        self.cipher = None
        self._carregar_ou_gerar_chave()

    def _carregar_ou_gerar_chave(self):
        if Path(self.arquivo_chave).exists():
            with open(self.arquivo_chave, "rb") as f:
                chave = f.read()
            print(f" Chave carregada de: {self.arquivo_chave}")
        else:
            # PILAR 1: CONFIDENCIALIDADE - Geração Segura de Chave
            # Gera uma chave criptograficamente segura de 256 bits (32 bytes em base64). 
            # A biblioteca cryptography utiliza os.urandom(), coletando entropia do sistema 
            # operacional, o que impede ataques de força bruta previsíveis.
            chave = Fernet.generate_key()
            with open(self.arquivo_chave, "wb") as f:
                f.write(chave)
            print(f" Nova chave gerada e salva em: {self.arquivo_chave}")
        
        # Inicializa o motor criptográfico simétrico com a chave carregada/gerada.
        self.cipher = Fernet(chave)

    def criptografar(self, dados: str) -> bytes:
        # A criptografia atua sobre bytes, não strings puras.
        dados_bytes = dados.encode("utf-8")
        
        # PILAR 1: CONFIDENCIALIDADE - Cifragem AES-128-CBC
        # O Fernet emprega internamente o padrão AES-128 no modo CBC (Cipher Block Chaining).
        # No modo CBC, cada bloco de dados é misturado (XOR) com o bloco anterior antes de ser cifrado,
        # ocultando padrões nos dados originais. O Fernet também inclui um timestamp e um HMAC.
        dados_cifrados = self.cipher.encrypt(dados_bytes)
        return dados_cifrados

    def descriptografar(self, dados_cifrados: bytes) -> str:
        # Processo de reversão da cifra.
        # O Fernet verifica automaticamente a assinatura HMAC antes de tentar descriptografar.
        # Se o dado foi corrompido ou adulterado, a descriptografia é abortada por segurança.
        dados_bytes = self.cipher.decrypt(dados_cifrados)
        return dados_bytes.decode("utf-8")

    def criptografar_arquivo(self, caminho_entrada: str, caminho_saida: str):
        # Proteção de Dados em Repouso (Data at Rest):
        # Lê o conteúdo de um arquivo em texto claro e grava uma cópia ilegível (.enc).
        # Sem a chave_secreta.key, o invasor vê apenas bytes embaralhados.
        with open(caminho_entrada, "r", encoding="utf-8") as f:
            conteudo = f.read()
        cifrado = self.criptografar(conteudo)
        with open(caminho_saida, "wb") as f:
            f.write(cifrado)
        print(f" Arquivo normal '{caminho_entrada}' Arquivo cifrado -> '{caminho_saida}'")

    def descriptografar_arquivo(self, caminho_cifrado: str) -> str:
        # Lê os bytes cifrados do disco e aplica o processo de recuperação para memória.
        with open(caminho_cifrado, "rb") as f:
            cifrado = f.read()
        return self.descriptografar(cifrado)

def demo_confidencialidade():
    separador("CONFIDENCIALIDADE (Fernet / AES-128-CBC)")
    conf = GerenciadorConfidencialidade()

    mensagem_original = "Senha do banco: S3cr3t@2024 | CPF: 123.456.789-00"
    print(f"\n  Dados originais    : {mensagem_original}")

    cifrado = conf.criptografar(mensagem_original)
    print(f"  Dados cifrados     : {cifrado[:60]}...")

    recuperado = conf.descriptografar(cifrado)
    print(f"  Dados recuperados  : {recuperado}")

    with open("dados_sensiveis.txt", "w", encoding="utf-8") as f:
        f.write("Relatorio confidencial - NAO COMPARTILHAR\nDados sigilosos aqui.")

    conf.criptografar_arquivo("dados_sensiveis.txt", "dados_sensiveis.enc")
    conteudo_decifrado = conf.descriptografar_arquivo("dados_sensiveis.enc")
    print(f"\n  Arquivo recuperado :\n  {conteudo_decifrado}")
    print("\n  Confidencialidade garantida: sem a chave, os dados sao ilegíveis.")

if __name__ == "__main__":
    pasta_do_script = os.path.dirname(os.path.abspath(__file__))
    os.chdir(pasta_do_script)

    print("  APLICACAO DE SEGURANCA DA INFORMACAO - CONFIDENCIALIDADE")
    print("  Alunas: Desiree, Ana, Isabelle, Nicole, Giovana Marsigli, Mariana Akemi")
    demo_confidencialidade()
