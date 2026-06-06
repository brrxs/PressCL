Set fso   = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
root = fso.GetParentFolderName(WScript.ScriptFullName)

' If already running, just open the browser
portCheck = shell.Run("cmd /c netstat -an | find "":8501 "" > nul 2>&1", 0, True)
If portCheck <> 0 Then
    shell.Run "cmd /c cd /d """ & root & """ && .venv\Scripts\streamlit run app.py --server.headless true", 0, False
    WScript.Sleep 4000
End If

shell.Run "http://localhost:8501"
