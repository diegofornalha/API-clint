#!/usr/bin/env python3
"""
Script para verificar o status da migração do Gradio para Streamlit.
Este script mostra um resumo do status atual da migração.
"""

import os
import sys
from pathlib import Path

def check_red(text):
    """Retorna texto em vermelho"""
    return f"\033[91m{text}\033[0m"

def check_green(text):
    """Retorna texto em verde"""
    return f"\033[92m{text}\033[0m"

def check_yellow(text):
    """Retorna texto em amarelo"""
    return f"\033[93m{text}\033[0m"

def check_files_exist():
    """Verifica a existência de arquivos importantes"""
    files_to_check = {
        "Interface Streamlit": "streamlit_audio_interface.py",
        "Script de Teste": "test_streamlit_interface.py",
        "Plano de Migração": "MIGRATION.md",
        "README Atualizado": "README.md",
    }
    
    results = {}
    for name, file_path in files_to_check.items():
        exists = os.path.exists(file_path)
        results[name] = exists
        status = check_green("✅ Presente") if exists else check_red("❌ Ausente")
        print(f"{name}: {status}")
    
    return all(results.values())

def check_gradio_removed():
    """Verifica se o Gradio foi removido"""
    gradio_file = "gradio_audio_interface.py"
    removed = not os.path.exists(gradio_file)
    status = check_green("✅ Removido") if removed else check_red("❌ Ainda presente")
    print(f"Arquivo Gradio: {status}")
    return removed

def check_requirements():
    """Verifica se Streamlit está nos requisitos"""
    req_file = "requirements.txt"
    if not os.path.exists(req_file):
        print(f"Arquivo requirements.txt: {check_red('❌ Não encontrado')}")
        return False
    
    with open(req_file, 'r') as f:
        content = f.read().lower()
    
    has_streamlit = 'streamlit' in content
    status = check_green("✅ Presente") if has_streamlit else check_red("❌ Ausente")
    print(f"Streamlit nos requisitos: {status}")
    return has_streamlit

def summarize():
    """Resumo da verificação"""
    print("\n----- RESUMO DA MIGRAÇÃO -----")
    
    files_exist = check_files_exist()
    print()
    
    gradio_removed = check_gradio_removed()
    print()
    
    requirements_updated = check_requirements()
    print()
    
    # Verifica status geral
    if files_exist and gradio_removed and requirements_updated:
        print(check_green("✅ Migração concluída com sucesso!"))
    elif files_exist and requirements_updated:
        print(check_yellow("⚠️ Migração parcialmente concluída."))
    else:
        print(check_red("❌ A migração não foi concluída."))
    
    # Próximos passos
    print("\n----- PRÓXIMOS PASSOS -----")
    if not files_exist:
        print("1. Criar os arquivos necessários para a interface Streamlit")
    
    if not gradio_removed:
        print("1. Remover o arquivo Gradio (gradio_audio_interface.py)")
    
    if not requirements_updated:
        print("1. Atualizar requirements.txt para incluir Streamlit")
    
    if files_exist and gradio_removed and requirements_updated:
        print("O processo de migração está concluído! Para testar a interface Streamlit, execute:")
        print(check_green("  streamlit run streamlit_audio_interface.py"))

if __name__ == "__main__":
    print("\n===== VERIFICAÇÃO DE MIGRAÇÃO GRADIO -> STREAMLIT =====\n")
    summarize()
    print("\n=====================================================\n") 