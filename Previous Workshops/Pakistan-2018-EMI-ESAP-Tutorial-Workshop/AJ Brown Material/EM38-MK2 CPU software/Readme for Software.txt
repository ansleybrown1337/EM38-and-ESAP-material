The password to unzip the processing file DAT38MK2 is "apple" and 
s/n is m38160812201 - 2017
s/n = M38180312701 - as of 08/02/18

Below is a link that explains the data output:
http://www.geonics.com/pdfs/computerinterface/em38-mk2_Interface.pdf

If the s/n DOES NOT work, 
Most likely the software has updated and a new one will have to be obtained by calling geonics (Mike Catalano)

If error occurs in the DAT38mk2 program when using "convert" function along the lines of"
"Component 'MSCOMCTL.OCX' or one of its dependencies not correctly registered: a file is missing or invalid."

Follow these steps for each component missing:
	Search for where Command Prompt is located on windows
	Right click on Command Prompt and select Run As Administrator
	Type the following
	CD C:\Windows\SysWOW64 directory
	Press Enter
	Next Type
	Regsvr32 MSCOMCTL.OCX
	Press Enter
	You should get a message "DllRegisterServer in mscomctl.ocx succeeded"