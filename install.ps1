# Richiesta di elevazione dei privilegi
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Start-Process powershell.exe "-File",($MyInvocation.MyCommand.Definition) -Verb RunAs
    exit
}

# Navigazione alla directory dello script (opzionale, dipende dalla necessità)
# Set-Location -Path "C:\Percorso\Alla\Directory\Dello\Script"
Set-ExecutionPolicy RemoteSigned

# Creazione dell'ambiente virtuale Python e attivazione
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Installazione delle dipendenze da requirements.txt e requirements2.txt
pip install -r requirements.txt
pip install -r requirements2.txt

# Esecuzione di ulteriori comandi Python, ad esempio la creazione di una distribuzione wheel
python setup.py bdist_wheel

# Messaggio di completamento
Write-Host "Installazione completata. Usa '.\.\Scripts\Activate.ps1' per attivare l'ambiente virtuale."
