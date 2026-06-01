# -*- coding: utf-8 -*-
import os
import sys
import io
import json
import hmac
import hashlib
import datetime
from pathlib import Path
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def separador(titulo: str):
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print('='*60)

class GerenciadorIntegridade:
    def __init__(self, chave_hmac: str = "chave_hmac_secreta_2024"):
        # A chave secreta é essencial para o HMAC. Apenas quem possui esta chave
        # pode gerar um hash válido, garantindo a autenticidade da origem.
        self.chave_hmac = chave_hmac.encode("utf-8")

    # PILAR 2: INTEGRIDADE - SHA-256 Simples
    def calcular_sha256(self, dados: str) -> str:
        # Utiliza o algoritmo SHA-256 para gerar um "digest" único de 256 bits.
        # Devido ao efeito avalanche, qualquer alteração mínima nos dados de entrada
        # resultará em um hash completamente diferente na saída.
        return hashlib.sha256(dados.encode("utf-8")).hexdigest()

    def calcular_sha256_arquivo(self, caminho: str) -> str:
        sha256 = hashlib.sha256()
        # Lê o arquivo em blocos de 64KB (65536 bytes) em vez de carregar tudo na memória.
        # Excelente prática para lidar com arquivos grandes sem travar o sistema.
        with open(caminho, "rb") as f:
            while bloco := f.read(65536):
                sha256.update(bloco)
        return sha256.hexdigest()

    # PILAR 2: INTEGRIDADE - Autenticação de Mensagens com HMAC-SHA256
    def calcular_hmac(self, dados: str) -> str:
        # Combina o algoritmo SHA-256 com a chave secreta.
        # Isso protege contra ataques onde um invasor forja os dados e recalcula o hash,
        # pois o invasor não possui a chave para gerar o MAC correto.
        return hmac.new(
            self.chave_hmac,
            dados.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

    def verificar_integridade(self, dados: str, hash_esperado: str, metodo: str = "sha256") -> bool:
        if metodo == "sha256":
            hash_atual = self.calcular_sha256(dados)
        elif metodo == "hmac":
            hash_atual = self.calcular_hmac(dados)
        else:
            raise ValueError(f"Metodo desconhecido: {metodo}")
        
        # Uso crítico do hmac.compare_digest():
        # Realiza a comparação de strings em "tempo constante".
        # Isso elimina vulnerabilidades de 'timing attack' (ataques que medem o tempo de 
        # comparação caractere por caractere para tentar deduzir o hash/chave correta).
        return hmac.compare_digest(hash_atual, hash_esperado)

    def salvar_manifesto(self, arquivos: list, caminho_manifesto: str):
        # Cria um arquivo JSON com os hashes originais de um grupo de arquivos.
        # Serve como uma "foto" do estado íntegro dos arquivos no momento da geração.
        manifesto = {
            "gerado_em": datetime.datetime.now().isoformat(),
            "arquivos": {}
        }
        for arq in arquivos:
            if Path(arq).exists():
                manifesto["arquivos"][arq] = self.calcular_sha256_arquivo(arq)
        with open(caminho_manifesto, "w", encoding="utf-8") as f:
            json.dump(manifesto, f, indent=2, ensure_ascii=False)
        print(f"  [INTEG] Manifesto salvo em: {caminho_manifesto}")
        return manifesto

    def verificar_manifesto(self, caminho_manifesto: str) -> dict:
        # Compara os hashes atuais dos arquivos com os hashes salvos no manifesto.
        # Ideal para detectar arquivos corrompidos ou modificados por malwares/invasores.
        with open(caminho_manifesto, "r", encoding="utf-8") as f:
            manifesto = json.load(f)
        resultados = {}
        for arq, hash_esperado in manifesto["arquivos"].items():
            if not Path(arq).exists():
                resultados[arq] = "ARQUIVO NAO ENCONTRADO"
            else:
                hash_atual = self.calcular_sha256_arquivo(arq)
                ok = hmac.compare_digest(hash_atual, hash_esperado)
                resultados[arq] = "OK" if ok else "CORROMPIDO"
        return resultados

def demo_integridade():
    separador("INTEGRIDADE (SHA-256 + HMAC-SHA256)")
    integ = GerenciadorIntegridade()

    mensagem = "Transferencia bancaria: R$ 1.000,00 para conta 12345"
    print(f"\n  Mensagem           : {mensagem}")

    hash_sha = integ.calcular_sha256(mensagem)
    print(f"  SHA-256            : {hash_sha}")

    hash_hmac = integ.calcular_hmac(mensagem)
    print(f"  HMAC-SHA256        : {hash_hmac}")

    ok = integ.verificar_integridade(mensagem, hash_sha, "sha256")
    print(f"\n  Verificacao (original): {'INTEGRA' if ok else 'CORROMPIDA'}")

    mensagem_adulterada = "Transferencia bancaria: R$ 9.999,99 para conta 99999"
    ok2 = integ.verificar_integridade(mensagem_adulterada, hash_sha, "sha256")
    print(f"  Verificacao (adulterada): {'INTEGRA' if ok2 else 'CORROMPIDA - adulteracao detectada!'}")

    arquivos = ["dados_sensiveis.txt", "dados_sensiveis.enc"]
    arquivos_existentes = [a for a in arquivos if Path(a).exists()]
    if arquivos_existentes:
        integ.salvar_manifesto(arquivos_existentes, "manifesto_integridade.json")
        resultados = integ.verificar_manifesto("manifesto_integridade.json")
        print(f"\n  Verificacao de manifesto:")
        for arq, status in resultados.items():
            print(f"    {arq}: {status}")

    print("\n  Integridade garantida: qualquer alteracao nos dados e detectada.")

if __name__ == "__main__":
    pasta_do_script = os.path.dirname(os.path.abspath(__file__))
    os.chdir(pasta_do_script)

    print("  APLICACAO DE SEGURANCA DA INFORMACAO - INTEGRIDADE")
    print("  Alunas: Desiree, Ana, Isabelle, Nicole, Giovana Marsigli, Mariana Akemi")
    demo_integridade()
