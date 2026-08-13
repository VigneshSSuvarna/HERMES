import win32com.client
import os
from .base_connector import HermesConnector

class OfficeConnector(HermesConnector):
    def get_supported_actions(self):
        return ["write_excel"]

    def execute(self, action_type: str, target: str) -> str:
        # Target format expected from AI: "C:\path\to\file.xlsx|A1|Hello World"
        try:
            parts = target.split("|")
            if len(parts) < 3: return "Error: Target must be 'filepath|cell|value'"
            
            filepath = os.path.abspath(parts[0].strip())
            cell = parts[1].strip()
            value = parts[2].strip()

            # Connect to Excel
            excel = win32com.client.Dispatch("Excel.Application")
            excel.Visible = True # Show the user the magic happening
            
            if not os.path.exists(filepath):
                wb = excel.Workbooks.Add()
                wb.SaveAs(filepath)
            else:
                wb = excel.Workbooks.Open(filepath)
                
            sheet = wb.ActiveSheet
            sheet.Range(cell).Value = value
            wb.Save()
            
            return f"Successfully wrote '{value}' to cell {cell} in {os.path.basename(filepath)}."
        except Exception as e:
            return f"Office Automation Error: {e}"