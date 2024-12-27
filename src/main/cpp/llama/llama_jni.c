#include <jni.h>
#include "llama.h"
#include <string>

extern "C" {

JNIEXPORT jlong JNICALL Java_ugen_org_llm_LlamaProvider_initializeModel
  (JNIEnv* env, jobject obj, jstring modelPath) {
    const char* path = env->GetStringUTFChars(modelPath, 0);
    
    llama_context_params params = llama_context_default_params();
    llama_context* ctx = llama_init_from_file(path, params);
    
    env->ReleaseStringUTFChars(modelPath, path);
    return (jlong)ctx;
}

JNIEXPORT jstring JNICALL Java_ugen_org_llm_LlamaProvider_generate
  (JNIEnv* env, jobject obj, jlong contextPtr, jstring prompt) {
    llama_context* ctx = (llama_context*)contextPtr;
    const char* input = env->GetStringUTFChars(prompt, 0);
    
    std::string output = llama_generate(ctx, input);
    
    env->ReleaseStringUTFChars(prompt, input);
    return env->NewStringUTF(output.c_str());
}

JNIEXPORT void JNICALL Java_ugen_org_llm_LlamaProvider_freeModel
  (JNIEnv* env, jobject obj, jlong contextPtr) {
    llama_context* ctx = (llama_context*)contextPtr;
    llama_free(ctx);
}

}