import streamlit as st
import google.generativeai as genai
import pandas as pd
import json
import io

st.set_page_config(page_title="Extrator Pro do Google Maps", page_icon="📍", layout="wide")

st.title("📍 Extrator Pro de Leads - Google Maps v2.0")
st.markdown("Cole o texto bruto copiado do Google Maps para estruturar e gerar uma planilha Excel perfeita (.xlsx).")

# Sidebar - Configurações
with st.sidebar:
    st.header("⚙️ Configurações")
    api_key = st.text_input("Cole sua Gemini API Key:", type="password")

texto_bruto = st.text_area("Cole aqui o texto copiado do Google Maps:", height=300, placeholder="Cole todo o texto da página aqui...")

if st.button("🚀 Extrair e Gerar Planilha", type="primary"):
    if not api_key:
        st.error("Por favor, insira sua API Key do Gemini na barra lateral.")
    elif not texto_bruto.strip():
        st.warning("Por favor, cole o texto do Google Maps na caixa de texto.")
    else:
        try:
            with st.spinner("Processando e limpando os dados com IA..."):
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-2.5-flash")
                
                prompt = f"""
                Você é um assistente especialista em extração de dados e engenharia de dados.
                Analise o texto bruto fornecido abaixo, copiado diretamente do Google Maps, e extraia TODAS as empresas listadas.

                Instruções rigorosas de extração:
                1. Extraia CADA empresa encontrada no texto sem omitir nenhuma.
                2. Para cada empresa, identifique:
                   - nome_empresa: Nome completo exato da empresa.
                   - categoria: Categoria ou ramo principal de atuação.
                   - telefone_fixo: Telefone comercial/fixo se houver.
                   - whatsapp: Número de celular/WhatsApp se houver.
                   - email: E-mail de contato se houver (caso contrário null).
                   - website: Endereço do site se houver (caso contrário null).
                   - endereco_completo: Logradouro, número, bairro.
                   - cidade: Nome da cidade.
                   - estado: Sigla do estado (ex: SP).
                   - avaliacao: Nota média (ex: 4.8).
                   - num_avaliacoes: Quantidade total de avaliações.
                   - produtos_servicos: Resumo das especialidades, produtos fabricados ou serviços mencionados.

                Regra de Formato:
                Retorne EXCLUSIVAMENTE um array JSON válido contendo os objetos de cada empresa.
                Não inclua explicações, textos introdutórios ou tags de markdown de código.
                Garantir acentuação correta em português (UTF-8).

                TEXTO BRUTO DO GOOGLE MAPS:
                {texto_bruto}
                """

                response = model.generate_content(prompt)
                raw_response = response.text.strip()
                
                if raw_response.startswith("```"):
                    raw_response = raw_response.split("```")[1]
                    if raw_response.startswith("json"):
                        raw_response = raw_response[4:]
                raw_response = raw_response.strip()

                dados = json.loads(raw_response)
                df = pd.DataFrame(dados)

                st.success(f"✅ Sucesso! Foram extraídas **{len(df)}** empresas.")

                # Exibição na tela
                st.dataframe(df, use_container_width=True)

                # Criação do arquivo Excel (.xlsx real em memória)
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Leads Google Maps')
                excel_data = output.getvalue()

                # Botão de Download em Excel Nativo (.xlsx)
                st.download_button(
                    label="📥 Baixar Planilha Excel (.xlsx)",
                    data=excel_data,
                    file_name="leads_google_maps.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        except Exception as e:
            st.error(f"Ocorreu um erro ao processar os dados: {e}")
