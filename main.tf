variable "folder_id" {
    type = string
}

variable "service_account_id" {
    type = string
}

variable "api_image_url" {
    type = string
}

terraform {
    required_version = ">= 1.3.0"

    required_providers {
        yandex = {
            source  = "yandex-cloud/yandex"
            version = "~> 0.130"
        }
    }
}

provider "yandex" {
    folder_id = var.folder_id
}

resource "yandex_serverless_container" "greendata_api" {
    name               = "greendata_api"
    folder_id          = var.folder_id
    service_account_id = var.service_account_id

    cores       = 4
    memory      = 4096
    concurrency = 1

    image {
        url = var.api_image_url
    }
}