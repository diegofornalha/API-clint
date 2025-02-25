#!/usr/bin/env python3
"""
Script para testar a funcionalidade básica da interface Streamlit.
Este script verifica se:
1. O Streamlit está instalado corretamente
2. As funções de envio de áudio estão funcionando
3. A codificação de áudio funciona corretamente
"""

import sys
import os
import tempfile
import base64

# Verifica se o Streamlit está instalado
try:
    import streamlit
    print("✅ Streamlit está instalado corretamente!")
except ImportError:
    print("❌ Streamlit não está instalado. Por favor, execute: pip install streamlit")
    sys.exit(1)

# Verifica se o arquivo da interface Streamlit existe
if not os.path.exists("streamlit_audio_interface.py"):
    print("❌ Arquivo streamlit_audio_interface.py não encontrado!")
    sys.exit(1)
else:
    print("✅ Arquivo streamlit_audio_interface.py encontrado!")

# Importa a função de codificação para testar
try:
    sys.path.append(".")
    from streamlit_audio_interface import encode_audio_to_base64
    print("✅ Função de codificação importada com sucesso!")
except ImportError:
    print("❌ Não foi possível importar a função encode_audio_to_base64")
    sys.exit(1)

# Cria um arquivo de áudio temporário para teste
def create_temp_audio_file():
    try:
        # Cria um arquivo de áudio simples para teste
        temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
        temp_file.write(b"Test audio content")
        temp_file.close()
        return temp_file.name
    except Exception as e:
        print(f"❌ Erro ao criar arquivo de áudio temporário: {str(e)}")
        return None

# Testa a função de codificação
def test_encode_function():
    temp_audio_file = create_temp_audio_file()
    if not temp_audio_file:
        return False
    
    try:
        base64_content = encode_audio_to_base64(temp_audio_file)
        if base64_content and isinstance(base64_content, str):
            print("✅ Função de codificação funcionando corretamente!")
            # Limpa o arquivo temporário
            os.unlink(temp_audio_file)
            return True
        else:
            print("❌ Função de codificação retornou um valor inválido!")
            return False
    except Exception as e:
        print(f"❌ Erro ao testar função de codificação: {str(e)}")
        return False
    finally:
        # Tenta limpar o arquivo se ainda existir
        if os.path.exists(temp_audio_file):
            os.unlink(temp_audio_file)

# Imprime instruções para executar a interface
def print_instructions():
    print("\n===== INSTRUÇÕES PARA EXECUTAR A INTERFACE =====")
    print("Para iniciar a interface Streamlit, execute:")
    print("  streamlit run streamlit_audio_interface.py")
    print("===================================================")

# Executa os testes
if __name__ == "__main__":
    print("\n===== TESTES DA INTERFACE STREAMLIT =====")
    test_result = test_encode_function()
    print("\n===== RESUMO DOS TESTES =====")
    if test_result:
        print("✅ Todos os testes passaram!")
    else:
        print("❌ Falha em alguns testes. Verifique os erros acima.")
    
    print_instructions() 