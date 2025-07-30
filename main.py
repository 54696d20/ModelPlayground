import os
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForCausalLM

import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic models
class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: int = 512

class GenerateResponse(BaseModel):
    generated_code: str

class ChatRequest(BaseModel):
    message: str
    max_tokens: int = 512
    session_id: str = "default"  # To track different conversations

class ChatResponse(BaseModel):
    response: str
    session_id: str

class HealthResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    status: str
    model_loaded: bool
    device: str

# Global variables for model and tokenizer
model = None
tokenizer = None
device = None
model_type = None  # Track if it's a seq2seq or causal model

# Conversation memory - store conversation history
conversation_history = {}

app = FastAPI(
    title="Code Generation API",
    description="A FastAPI service for code generation using Hugging Face models",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_model():
    """Load the model and tokenizer based on environment variables"""
    global model, tokenizer, device, model_type
    
    model_name = os.getenv("MODEL_NAME", "Qwen/Qwen1.5-0.5B-Chat")
    device_name = os.getenv("DEVICE", "auto")
    
    if device_name == "auto":
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = device_name
    
    logger.info(f"Loading model: {model_name}")
    logger.info(f"Using device: {device}")
    
    try:
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Load as causal model with CPU optimization
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True,
            device_map="auto",
            offload_folder="offload"
        )
        model_type = "causal"
        logger.info(f"Loaded {model_name} as causal model")
        
        # When using device_map="auto", don't manually move the model
        
        # Set pad token if not present
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        
        logger.info(f"Model {model_name} loaded successfully on {device} as {model_type}")
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise e

@app.on_event("startup")
async def startup_event():
    """Initialize the model on startup"""
    load_model()
    logger.info(f"Code Generation API started on port 8000")
    logger.info(f"Model loaded: {os.getenv('MODEL_NAME', 'Qwen/Qwen1.5-0.5B-Chat')}")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        model_loaded=model is not None,
        device=device or "unknown"
    )

@app.get("/conversations")
async def list_conversations():
    """List all active conversation sessions"""
    return {
        "sessions": list(conversation_history.keys()),
        "total_sessions": len(conversation_history)
    }

@app.delete("/conversations/{session_id}")
async def clear_conversation(session_id: str):
    """Clear a specific conversation session"""
    if session_id in conversation_history:
        del conversation_history[session_id]
        return {"message": f"Conversation {session_id} cleared"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.delete("/conversations")
async def clear_all_conversations():
    """Clear all conversation sessions"""
    global conversation_history
    conversation_history = {}
    return {"message": "All conversations cleared"}

@app.post("/generate", response_model=GenerateResponse)
async def generate_code(request: GenerateRequest):
    """Generate code based on the provided prompt"""
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        start_time = time.time()
        
        # Add code generation context to the prompt
        code_prompt = f"Generate Python code for: {request.prompt}"
        
        # Encode the input prompt with attention mask
        inputs = tokenizer(code_prompt, return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate code based on model type
        with torch.no_grad():
            if model_type == "seq2seq":
                # For seq2seq models (T5-style), use the full prompt
                outputs = model.generate(
                    inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    max_length=inputs["input_ids"].shape[1] + request.max_tokens,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id
                )
                # For seq2seq, the output is the complete generated text
                generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                # Extract only the generated part (remove the input prompt)
                generated_code = generated_text[len(code_prompt):].strip()
                # Clean up code response
                if "```" in generated_code:
                    generated_code = generated_code.split("```")[0].strip()
            else:
                # For causal models (GPT-style), use the full prompt
                outputs = model.generate(
                    inputs["input_ids"],
                    attention_mask=inputs["attention_mask"],
                    max_length=inputs["input_ids"].shape[1] + request.max_tokens,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id,
                    eos_token_id=tokenizer.eos_token_id
                )
                # For causal models, the output includes the input
                generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                # Extract only the generated part (remove the input prompt)
                generated_code = generated_text[len(code_prompt):].strip()
                # Clean up code response
                if "```" in generated_code:
                    generated_code = generated_code.split("```")[0].strip()
        
        generation_time = time.time() - start_time
        
        logger.info(f"Generated code in {generation_time:.2f}s")
        logger.info(f"Input prompt length: {len(request.prompt)}")
        logger.info(f"Generated code length: {len(generated_code)}")
        logger.info(f"Model type: {model_type}")
        
        return GenerateResponse(generated_code=generated_code)
        
    except Exception as e:
        logger.error(f"Error during code generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Code generation failed: {str(e)}")

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the model"""
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        start_time = time.time()
        
        # Get or create conversation history for this session
        if request.session_id not in conversation_history:
            conversation_history[request.session_id] = []
        
        # Add the new message to conversation history
        conversation_history[request.session_id].append(f"User: {request.message}")
        
                # Build the full conversation context
        conversation_context = "\n".join(conversation_history[request.session_id])
        chat_prompt = f"{conversation_context}\nAssistant:"
        
        # Encode the input message with attention mask
        inputs = tokenizer(chat_prompt, return_tensors="pt", padding=True, truncation=True)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=inputs["input_ids"].shape[1] + request.max_tokens,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id
            )
        
        # Decode the generated text
        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only the generated part (remove the input prompt)
        response = generated_text[len(chat_prompt):].strip()
        
        # Clean up the response
        if response:
            # Remove any trailing "User:" or similar
            response = response.split("User:")[0].strip()
            response = response.split("Assistant:")[0].strip()
        else:
            response = "I'm not sure how to respond to that."
        
        # Add the assistant's response to conversation history
        conversation_history[request.session_id].append(f"Assistant: {response}")
        
        # Keep only the last 10 messages to prevent context from getting too long
        if len(conversation_history[request.session_id]) > 10:
            conversation_history[request.session_id] = conversation_history[request.session_id][-10:]
        
        generation_time = time.time() - start_time
        
        logger.info(f"Chat response generated in {generation_time:.2f}s")
        logger.info(f"Session: {request.session_id}")
        logger.info(f"Input message: {request.message}")
        logger.info(f"Response: {response}")
        logger.info(f"Conversation length: {len(conversation_history[request.session_id])}")
        
        return ChatResponse(response=response, session_id=request.session_id)
        
    except Exception as e:
        logger.error(f"Error during chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 