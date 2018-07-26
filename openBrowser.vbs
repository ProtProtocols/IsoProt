
URL = WScript.Arguments.Item(0)
'URL = "http://localhost:8889"



Function Test_server()

    Set httpRequest = CreateObject("Microsoft.XMLHTTP")
    
    On Error resume next:

    With httpRequest
        .Open "HEAD", URL, False
      ' .setRequestHeader "If-Modified-Since", "Sat, 1 Jan 2000 00:00:00 GMT"
      ' .setRequestHeader "Content-Type", "application/x-www-form-urlencoded"
        .send
    End With
    
    if Err.Number <> 0 then
        Test_server = False
        Exit Function
     end if

    Test_server = True   
    
end Function


' Try to contact server for 5 times and open web browser if it's possible

' Note, function Test_server sometimes takes longer (about sec).

MAX_TRYS = 1000
for i=1 to MAX_TRYS
    server_active = Test_server()
    if server_active then 
        ' open browser
        CreateObject("WScript.Shell").Run "%comspec% /c start "+URL, 0, True
        Wscript.Quit 0
    end if
	Wscript.sleep 100
Next

Wscript.echo "Can't open the browser"







