import sys
import io
import os
import time
import json
import shutil
import datetime
import functools
import threading
from pathlib import Path
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def separador(titulo: str):
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print('='*60)

class RateLimiter:
    def __init__(self, max_requisicoes: int = 5, janela_segundos: int = 10):
        self.max_requisicoes = max_requisicoes
        self.janela_segundos = janela_segundos
        self.historico: dict = defaultdict(list)
        self._lock = threading.Lock()

    def verificar(self, usuario: str) -> tuple:
        agora = time.time()
        with self._lock:
            self.historico[usuario] = [
                t for t in self.historico[usuario]
                if agora - t < self.janela_segundos
            ]
            contagem = len(self.historico[usuario])
            if contagem >= self.max_requisicoes:
                mais_antigo = self.historico[usuario][0]
                espera = self.janela_segundos - (agora - mais_antigo)
                return False, (f"Rate limit atingido: {contagem}/{self.max_requisicoes} "
                               f"req. Aguarde {espera:.1f}s")
            self.historico[usuario].append(agora)
            restantes = self.max_requisicoes - contagem - 1
            return True, f"OK - {restantes} requisicoes restantes na janela"

def retry_automatico(max_tentativas: int = 3, espera_base: float = 1.0, backoff_exponencial: bool = True):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            ultima_excecao = None
            for tentativa in range(1, max_tentativas + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    ultima_excecao = e
                    if tentativa < max_tentativas:
                        espera = espera_base * (2 ** (tentativa - 1)) if backoff_exponencial else espera_base
                        print(f"  [DISP] Tentativa {tentativa} falhou: {e}. Aguardando {espera:.1f}s...")
                        time.sleep(espera)
                    else:
                        print(f"  [DISP] Todas as {max_tentativas} tentativas falharam.")
            raise ultima_excecao
        return wrapper
    return decorator

class GerenciadorBackup:
    def __init__(self, diretorio_backup: str = "backups"):
        self.diretorio_backup = Path(diretorio_backup)
        self.diretorio_backup.mkdir(exist_ok=True)

    def criar_backup(self, arquivo_origem: str) -> str:
        origem = Path(arquivo_origem)
        if not origem.exists():
            raise FileNotFoundError(f"Arquivo nao encontrado: {arquivo_origem}")
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_backup = f"{origem.stem}_{timestamp}{origem.suffix}"
        destino = self.diretorio_backup / nome_backup
        shutil.copy2(str(origem), str(destino))
        print(f"  [DISP] Backup criado: {destino}")
        return str(destino)

    def listar_backups(self, nome_arquivo: str) -> list:
        prefixo = Path(nome_arquivo).stem
        backups = sorted(self.diretorio_backup.glob(f"{prefixo}_*"))
        return [str(b) for b in backups]

    def restaurar_ultimo_backup(self, nome_arquivo: str, destino: str = None) -> str:
        backups = self.listar_backups(nome_arquivo)
        if not backups:
            raise FileNotFoundError(f"Nenhum backup encontrado para: {nome_arquivo}")
        ultimo = backups[-1]
        destino = destino or nome_arquivo
        shutil.copy2(ultimo, destino)
        print(f"  [DISP] Arquivo restaurado de: {ultimo} -> {destino}")
        return destino

def demo_disponibilidade():
    separador("DISPONIBILIDADE (Rate Limiting + Retry + Backup)")

    print("\n  [A] Rate Limiting (5 req / 10s por usuario):")
    limiter = RateLimiter(max_requisicoes=5, janela_segundos=10)
    for i in range(7):
        permitido, msg = limiter.verificar("usuario_teste")
        status = "OK" if permitido else "BLOQUEADO"
        print(f"    Requisicao {i+1}: {status} | {msg}")

    print("\n  [B] Retry automatico com backoff exponencial:")
    contador = {"tentativas": 0}

    @retry_automatico(max_tentativas=3, espera_base=0.5)
    def operacao_instavel():
        contador["tentativas"] += 1
        if contador["tentativas"] < 3:
            raise ConnectionError("Servico temporariamente indisponivel")
        return "Operacao concluida com sucesso!"

    try:
        resultado = operacao_instavel()
        print(f"  [DISP]  Resultado: {resultado}")
    except Exception as e:
        print(f"  [DISP]  Falha definitiva: {e}")

    print("\n  [C] Backup automatico:")
    backup_mgr = GerenciadorBackup()

    arquivo_dados = "dados_importantes.json"
    dados = {"versao": 1, "conteudo": "Dados criticos do sistema", "ts": time.time()}
    with open(arquivo_dados, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2)

    backup_mgr.criar_backup(arquivo_dados)
    os.remove(arquivo_dados)
    print(f"  [DISP] Arquivo original removido (simula falha/ataque)")

    backup_mgr.restaurar_ultimo_backup(arquivo_dados)
    print(f"  [DISP] Arquivo restaurado com sucesso!")

    with open(arquivo_dados, encoding="utf-8") as f:
        recuperado = json.load(f)
    print(f"  [DISP] Conteudo recuperado: {recuperado['conteudo']}")
    print("\n  Disponibilidade garantida: rate limit, retry e backup protegem o sistema.")

if __name__ == "__main__":
    pasta_do_script = os.path.dirname(os.path.abspath(__file__))
    os.chdir(pasta_do_script)

    print("  APLICACAO DE SEGURANCA DA INFORMACAO - DISPONIBILIDADE")
    print("  Alunas: Desiree, Ana, Isabelle, Nicole, Giovana Marsigli, Mariana Akemi")
    demo_disponibilidade()