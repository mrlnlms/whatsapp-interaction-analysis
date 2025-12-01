# scripts/diagnose_embeddings.py
"""
Diagnóstico de Dimensionalidade dos Embeddings
"""

from sentence_transformers import SentenceTransformer

MODEL_NAME = 'paraphrase-multilingual-mpnet-base-v2'

print("="*80)
print("🔍 DIAGNÓSTICO DE EMBEDDINGS")
print("="*80)

# Carrega modelo
print(f"\n📦 Carregando: {MODEL_NAME}")
model = SentenceTransformer(MODEL_NAME)

# Informações do modelo
print(f"\n📊 Informações do Modelo:")
print(f"   Dimensões reportadas: {model.get_sentence_embedding_dimension()}")
print(f"   Max sequence length: {model.max_seq_length}")

# Informações da arquitetura
config = model._first_module().auto_model.config
print(f"\n🏗️  Arquitetura:")
print(f"   Model type: {config.model_type}")
print(f"   Hidden size: {config.hidden_size}")
print(f"   Num hidden layers: {config.num_hidden_layers}")
print(f"   Num attention heads: {config.num_attention_heads}")

# Pooling
print(f"\n🎯 Pooling Configuration:")
pooling = model._last_module()
print(f"   Pooling mode: {pooling.get_config_dict()}")
print(f"   Output dimension: {pooling.get_sentence_embedding_dimension()}")

# Teste prático
print(f"\n🧪 Teste Prático:")
test_text = "Teste de embedding"
embedding = model.encode([test_text])
print(f"   Input: '{test_text}'")
print(f"   Output shape: {embedding.shape}")
print(f"   Output dims: {embedding.shape[1]}")

# Conclusão
print(f"\n" + "="*80)
if embedding.shape[1] == 768:
    print("⚠️  CONCLUSÃO: Modelo está gerando 768 dimensões")
    print("\nPossíveis causas:")
    print("1. ✅ Modelo correto mas versão diferente (mpnet-base tem 768)")
    print("2. ✅ Hidden size padrão é 768, não 384")
    print("3. ✅ 'paraphrase-multilingual-mpnet-base-v2' pode ser variante 768d")
    print("\nNota: Modelos 'base' geralmente têm 768 dims.")
    print("      Modelos 'small' têm 384 dims.")
elif embedding.shape[1] == 384:
    print("✅ CONCLUSÃO: Modelo está gerando 384 dimensões (esperado)")
else:
    print(f"❓ CONCLUSÃO: Dimensão inesperada: {embedding.shape[1]}")

print("="*80)