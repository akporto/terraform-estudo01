# Nome único para identificar a função Lambda na AWS
variable "function_name" {
  description = "Nome da função Lambda"
  type        = string
}

variable "description" {
  description = "Descrição da função Lambda"
  type        = string
  default     = "Função criada pelo Terraform"
}

# Ponto de entrada da função Lambda (classe principal)
variable "handler" {
  description = "Handler da função Lambda (exemplo: index.handler)"
  type        = string
}

# Ambiente de execução da função Lambda
variable "runtime" {
  description = "Runtime da função Lambda"
  type        = string
  default     = "python3.9"
}

# Tempo máximo de execução da função em segundos
variable "timeout" {
  description = "Timeout da função Lambda em segundos"
  type        = number
  default     = 30
}

# Memória para a função Lambda em MB
variable "memory_size" {
  description = "Memória alocada para a função Lambda em MB"
  type        = number
  default     = 512
}


variable "artifact_path" {
  description = "Caminho para o arquivo da função Lambda"
  type        = string
}

# Variáveis de ambiente disponíveis durante a execução
variable "environment_variables" {
  description = "Variáveis de ambiente para a função Lambda"
  type        = map(string)
  default     = {}
}

# Tags para organização e rastreamento da função Lambda
variable "tags" {
  description = "Tags para a função Lambda"
  type        = map(string)
  default     = {}
}