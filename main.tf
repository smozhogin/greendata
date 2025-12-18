variable "folder_id" {
    type = string
}

variable "service_account_id" {
    type = string
}

variable "api_image_url" {
    type = string
}

resource "yandex_serverless_container" "greendata-api" {
    name               = "greendata-api"
    folder_id          = var.folder_id
    service_account_id = var.service_account_id

    cores       = 4
    memory      = 4096
    concurrency = 1

    image {
        url = var.api_image_url
    }
}