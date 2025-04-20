"""
Fine-tuning components for LLM models using LoRA and QLoRA
"""

import os
import json
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass

from ..utils.logger import LLMLogger, default_logger


@dataclass
class FineTuningConfig:
    """Configuration for fine-tuning"""
    
    # Base model configuration
    base_model: str
    output_dir: str
    
    # LoRA configuration
    lora_r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    
    # QLoRA specific configuration
    use_qlora: bool = False
    bits: int = 4
    quant_type: str = "nf4"
    
    # Training configuration
    batch_size: int = 4
    micro_batch_size: int = 1
    num_epochs: int = 3
    learning_rate: float = 3e-4
    cutoff_len: int = 256
    val_set_size: float = 0.1
    
    # Optimizer and scheduler
    optimizer: str = "adamw_torch"
    scheduler: str = "cosine"
    warmup_steps: int = 100
    
    # Gradient accumulation and clipping
    gradient_accumulation_steps: int = 1
    gradient_checkpointing: bool = True
    gradient_clip: float = 1.0
    
    # Mixed precision training
    fp16: bool = False
    bf16: bool = False
    
    # Miscellaneous
    seed: int = 42
    logging_steps: int = 10
    eval_steps: int = 100
    save_steps: int = 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {k: v for k, v in self.__dict__.items()}
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'FineTuningConfig':
        """Create config from dictionary"""
        return cls(**config_dict)
    
    def save(self, config_path: str):
        """Save config to file"""
        with open(config_path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, config_path: str) -> 'FineTuningConfig':
        """Load config from file"""
        with open(config_path, 'r') as f:
            config_dict = json.load(f)
        return cls.from_dict(config_dict)


class DatasetPreparation:
    """
    Prepare datasets for fine-tuning
    """
    
    def __init__(
        self,
        data_dir: str,
        output_dir: str,
        logger: Optional[LLMLogger] = None
    ):
        """
        Initialize dataset preparation
        
        Args:
            data_dir: Directory containing raw data
            output_dir: Directory to save processed data
            logger: Custom logger instance
        """
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.logger = logger or default_logger
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        self.logger.info(f"Dataset preparation initialized. Data dir: {data_dir}, Output dir: {output_dir}")
    
    def prepare_instruction_dataset(
        self,
        input_file: str,
        output_file: str,
        instruction_key: str = "instruction",
        input_key: str = "input",
        output_key: str = "output",
        format_template: Optional[str] = None
    ) -> int:
        """
        Prepare instruction dataset for fine-tuning
        
        Args:
            input_file: Input JSON file with raw data
            output_file: Output file to save processed data
            instruction_key: Key for instruction field in input data
            input_key: Key for input field in input data
            output_key: Key for output field in input data
            format_template: Template for formatting data (if None, uses default)
            
        Returns:
            Number of examples processed
        """
        self.logger.info(f"Preparing instruction dataset from {input_file}")
        
        # Default template if none provided
        if format_template is None:
            format_template = (
                "### Instruction:\n{instruction}\n\n"
                "### Input:\n{input}\n\n"
                "### Response:\n{output}"
            )
        
        input_path = os.path.join(self.data_dir, input_file)
        output_path = os.path.join(self.output_dir, output_file)
        
        try:
            # Load input data
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            processed_data = []
            
            for item in data:
                instruction = item.get(instruction_key, "")
                input_text = item.get(input_key, "")
                output_text = item.get(output_key, "")
                
                # Format according to template
                formatted_text = format_template.format(
                    instruction=instruction,
                    input=input_text,
                    output=output_text
                )
                
                processed_data.append({
                    "text": formatted_text
                })
            
            # Save processed data
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2)
            
            self.logger.info(f"Processed {len(processed_data)} examples. Saved to {output_path}")
            return len(processed_data)
            
        except Exception as e:
            self.logger.error(f"Error preparing instruction dataset: {str(e)}")
            raise
    
    def prepare_chat_dataset(
        self,
        input_file: str,
        output_file: str,
        messages_key: str = "messages",
        role_key: str = "role",
        content_key: str = "content",
        system_template: str = "### System:\n{system_message}\n\n"
    ) -> int:
        """
        Prepare chat dataset for fine-tuning
        
        Args:
            input_file: Input JSON file with raw data
            output_file: Output file to save processed data
            messages_key: Key for messages array in input data
            role_key: Key for role field in messages
            content_key: Key for content field in messages
            system_template: Template for system messages
            
        Returns:
            Number of examples processed
        """
        self.logger.info(f"Preparing chat dataset from {input_file}")
        
        input_path = os.path.join(self.data_dir, input_file)
        output_path = os.path.join(self.output_dir, output_file)
        
        try:
            # Load input data
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            processed_data = []
            
            for item in data:
                messages = item.get(messages_key, [])
                
                if not messages:
                    continue
                
                conversation = ""
                
                # Process messages
                for msg in messages:
                    role = msg.get(role_key, "").lower()
                    content = msg.get(content_key, "")
                    
                    if role == "system":
                        conversation += system_template.format(system_message=content)
                    elif role == "user":
                        conversation += f"### User:\n{content}\n\n"
                    elif role == "assistant":
                        conversation += f"### Assistant:\n{content}\n\n"
                
                processed_data.append({
                    "text": conversation.strip()
                })
            
            # Save processed data
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(processed_data, f, indent=2)
            
            self.logger.info(f"Processed {len(processed_data)} conversations. Saved to {output_path}")
            return len(processed_data)
            
        except Exception as e:
            self.logger.error(f"Error preparing chat dataset: {str(e)}")
            raise


class FineTuningManager:
    """
    Manager for fine-tuning LLM models using LoRA and QLoRA
    """
    
    def __init__(
        self,
        config: FineTuningConfig,
        logger: Optional[LLMLogger] = None
    ):
        """
        Initialize fine-tuning manager
        
        Args:
            config: Fine-tuning configuration
            logger: Custom logger instance
        """
        self.config = config
        self.logger = logger or default_logger
        
        # Create output directory if it doesn't exist
        os.makedirs(config.output_dir, exist_ok=True)
        
        # Save configuration
        config_path = os.path.join(config.output_dir, "config.json")
        config.save(config_path)
        
        self.logger.info(f"Fine-tuning manager initialized for model: {config.base_model}")
        self.logger.info(f"Using {'QLoRA' if config.use_qlora else 'LoRA'} for fine-tuning")
    
    def prepare_training_args(self) -> Dict[str, Any]:
        """
        Prepare training arguments for fine-tuning
        
        Returns:
            Dictionary of training arguments
        """
        training_args = {
            "output_dir": self.config.output_dir,
            "num_train_epochs": self.config.num_epochs,
            "per_device_train_batch_size": self.config.micro_batch_size,
            "gradient_accumulation_steps": self.config.gradient_accumulation_steps,
            "learning_rate": self.config.learning_rate,
            "logging_steps": self.config.logging_steps,
            "evaluation_strategy": "steps",
            "eval_steps": self.config.eval_steps,
            "save_strategy": "steps",
            "save_steps": self.config.save_steps,
            "save_total_limit": 3,
            "load_best_model_at_end": True,
            "report_to": "tensorboard",
            "seed": self.config.seed,
            "data_seed": self.config.seed,
            "gradient_checkpointing": self.config.gradient_checkpointing,
            "max_grad_norm": self.config.gradient_clip,
            "optim": self.config.optimizer,
            "lr_scheduler_type": self.config.scheduler,
            "warmup_steps": self.config.warmup_steps,
        }
        
        # Add precision settings
        if self.config.fp16:
            training_args["fp16"] = True
        elif self.config.bf16:
            training_args["bf16"] = True
        
        return training_args
    
    def prepare_lora_config(self) -> Dict[str, Any]:
        """
        Prepare LoRA configuration
        
        Returns:
            Dictionary of LoRA configuration
        """
        lora_config = {
            "r": self.config.lora_r,
            "lora_alpha": self.config.lora_alpha,
            "lora_dropout": self.config.lora_dropout,
            "bias": "none",
            "task_type": "CAUSAL_LM",
        }
        
        # Add QLoRA specific settings
        if self.config.use_qlora:
            lora_config.update({
                "load_in_4bit": self.config.bits == 4,
                "load_in_8bit": self.config.bits == 8,
                "bnb_4bit_quant_type": self.config.quant_type if self.config.bits == 4 else None,
                "bnb_4bit_compute_dtype": "float16",
                "bnb_4bit_use_double_quant": True,
            })
        
        return lora_config
    
    def generate_training_script(self, dataset_path: str, output_script_path: str):
        """
        Generate a training script for fine-tuning
        
        Args:
            dataset_path: Path to the processed dataset
            output_script_path: Path to save the training script
        """
        self.logger.info(f"Generating training script at {output_script_path}")
        
        script_content = f"""#!/usr/bin/env python
# Fine-tuning script generated by LLM Monitor

import os
import json
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# Load configuration
config_path = "{os.path.join(self.config.output_dir, 'config.json')}"
with open(config_path, 'r') as f:
    config = json.load(f)

# Set device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {{device}}")

# Load dataset
dataset = load_dataset("json", data_files="{dataset_path}")
train_val = dataset["train"].train_test_split(
    test_size=config["val_set_size"], 
    seed=config["seed"]
)
train_data = train_val["train"]
val_data = train_val["test"]

print(f"Loaded {{len(train_data)}} training examples and {{len(val_data)}} validation examples")

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(config["base_model"])
tokenizer.pad_token = tokenizer.eos_token

# Tokenize function
def tokenize_function(examples):
    return tokenizer(
        examples["text"],
        truncation=True,
        max_length=config["cutoff_len"],
        padding="max_length",
    )

# Tokenize datasets
tokenized_train = train_data.map(tokenize_function, batched=True)
tokenized_val = val_data.map(tokenize_function, batched=True)

# Prepare model
if config["use_qlora"]:
    # QLoRA setup
    from transformers import BitsAndBytesConfig
    
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=config["bits"] == 4,
        load_in_8bit=config["bits"] == 8,
        bnb_4bit_quant_type=config["quant_type"] if config["bits"] == 4 else None,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    
    model = AutoModelForCausalLM.from_pretrained(
        config["base_model"],
        quantization_config=bnb_config,
        device_map="auto",
    )
    model = prepare_model_for_kbit_training(model)
else:
    # Standard LoRA setup
    model = AutoModelForCausalLM.from_pretrained(
        config["base_model"],
        device_map="auto",
    )

# Configure LoRA
lora_config = LoraConfig(
    r=config["lora_r"],
    lora_alpha=config["lora_alpha"],
    lora_dropout=config["lora_dropout"],
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
)

model = get_peft_model(model, lora_config)
model.print_trainable_parameters()

# Training arguments
training_args = TrainingArguments(
    output_dir=config["output_dir"],
    num_train_epochs=config["num_epochs"],
    per_device_train_batch_size=config["micro_batch_size"],
    gradient_accumulation_steps=config["gradient_accumulation_steps"],
    per_device_eval_batch_size=config["micro_batch_size"],
    learning_rate=config["learning_rate"],
    logging_steps=config["logging_steps"],
    evaluation_strategy="steps",
    eval_steps=config["eval_steps"],
    save_strategy="steps",
    save_steps=config["save_steps"],
    save_total_limit=3,
    load_best_model_at_end=True,
    report_to="tensorboard",
    seed=config["seed"],
    data_seed=config["seed"],
    gradient_checkpointing=config["gradient_checkpointing"],
    max_grad_norm=config["gradient_clip"],
    optim=config["optimizer"],
    lr_scheduler_type=config["scheduler"],
    warmup_steps=config["warmup_steps"],
    fp16=config.get("fp16", False),
    bf16=config.get("bf16", False),
)

# Data collator
data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

# Initialize trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_val,
    data_collator=data_collator,
)

# Train model
trainer.train()

# Save model
model.save_pretrained(os.path.join(config["output_dir"], "final_model"))
tokenizer.save_pretrained(os.path.join(config["output_dir"], "final_model"))

print("Fine-tuning completed successfully!")
"""
        
        with open(output_script_path, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        os.chmod(output_script_path, 0o755)
        
        self.logger.info(f"Training script generated at {output_script_path}")
    
    def generate_inference_script(self, output_script_path: str):
        """
        Generate an inference script for the fine-tuned model
        
        Args:
            output_script_path: Path to save the inference script
        """
        self.logger.info(f"Generating inference script at {output_script_path}")
        
        script_content = f"""#!/usr/bin/env python
# Inference script generated by LLM Monitor

import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel, PeftConfig

# Load configuration
model_path = "{os.path.join(self.config.output_dir, 'final_model')}"
base_model = "{self.config.base_model}"

# Set device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {{device}}")

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_path)

# Load model
if os.path.exists(os.path.join(model_path, "adapter_config.json")):
    # Load as LoRA model
    print("Loading LoRA model...")
    config = PeftConfig.from_pretrained(model_path)
    
    if "{self.config.use_qlora}" == "True" and "{self.config.bits}" == "4":
        # Load quantized model for QLoRA
        from transformers import BitsAndBytesConfig
        
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="{self.config.quant_type}",
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_use_double_quant=True,
        )
        
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model,
            quantization_config=bnb_config,
            device_map="auto",
        )
    else:
        # Load standard model for LoRA
        base_model = AutoModelForCausalLM.from_pretrained(
            base_model,
            device_map="auto",
        )
    
    model = PeftModel.from_pretrained(base_model, model_path)
else:
    # Load as full model
    print("Loading full model...")
    model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto")

model.eval()

def generate_response(prompt, max_length=512, temperature=0.7, top_p=0.9):
    """Generate a response from the model"""
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    
    with torch.no_grad():
        outputs = model.generate(
            inputs["input_ids"],
            max_length=max_length,
            temperature=temperature,
            top_p=top_p,
            do_sample=True,
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# Example usage
if __name__ == "__main__":
    while True:
        user_input = input("\\nEnter your prompt (or 'quit' to exit): ")
        
        if user_input.lower() == "quit":
            break
        
        response = generate_response(user_input)
        print(f"\\nResponse: {{response}}\\n")
"""
        
        with open(output_script_path, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        os.chmod(output_script_path, 0o755)
        
        self.logger.info(f"Inference script generated at {output_script_path}")
