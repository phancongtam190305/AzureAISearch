# Azure AI Search Starter

Bo khung nay giup ban thu Azure AI Search nhanh tren may local voi:

- Backend `FastAPI`
- Frontend tinh de goi API search
- Script tao index va nap du lieu mau
- Ho tro 2 cach xac thuc:
  - Entra ID qua `az login`
  - API key qua bien moi truong

## 1. Yeu cau

- Azure AI Search service
- Azure CLI da cai
- Python 3.12 cho project

Neu ban dung Entra ID, tai khoan can co mot trong cac quyen:

- `Search Service Contributor` de tao hoac cap nhat index
- `Search Index Data Contributor` de nap du lieu va query

## 2. Cau hinh

Tao file `.env` tu `.env.example` va dien:

- `AZURE_SEARCH_ENDPOINT`
- `AZURE_SEARCH_INDEX_NAME`
- `AZURE_SEARCH_API_KEY` neu ban muon dung key
- `AZURE_USE_RBAC=true` neu ban muon dung `az login`

## 3. Cai dependency

```powershell
C:\Users\Admin\scoop\apps\uv\current\uv.exe python install 3.12
C:\Users\Admin\scoop\apps\uv\current\uv.exe sync
```

## 4. Dang nhap Azure

Neu dung RBAC:

```powershell
.\scripts\login-azure.ps1
```

Script nay tu dong dung thu muc `.azure` trong project de luu Azure CLI config.

Neu ban chua co search service, co the tao bang script:

```powershell
.\scripts\create-search-service.ps1 -ResourceGroup rg-ai-search-demo -ServiceName tam-search-demo -Location southeastasia
```

## 5. Tao index va nap du lieu mau

```powershell
.\scripts\bootstrap-index.ps1
```

## 6. Chay app

```powershell
.\scripts\dev.ps1
```

Mo `http://127.0.0.1:8000`

## 7. Thu search

- Keyword mode: tim kiem van ban co ban
- Semantic mode: tra ve caption va answer neu index da bat semantic

## Cau truc

- `backend/app/main.py`: API va static hosting
- `backend/app/search_service.py`: ket noi Azure AI Search
- `backend/scripts/bootstrap_index.py`: tao index va nap du lieu mau
- `frontend/`: giao dien dem nhanh de thu search
- `data/sample-docs.json`: du lieu mau bang tieng Viet
