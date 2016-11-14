set barcode_script_location to "/Users/robjwells/Projects/star-barcode/star_barcode.py"

set barcode_options to {"Tomorrow", "Another date", "Special sequence"}
set default_barcode to {"Tomorrow"}
set choice_message to "Which barcode do you want to create?"
set dialog_title to "Star Barcode"

set barcode_choice to (choose from list barcode_options default items default_barcode with prompt choice_message with title dialog_title) as string
if result is false then error number -128

if barcode_choice is in {"Tomorrow", "Another date"} then
    if barcode_choice is "Another date" then
        set edition_date to text returned of (display dialog "Please enter the barcode date in the format 2000-12-31:" default answer "")
    else
        set edition_date to do shell script "date -jv+1d +%Y-%m-%d"
    end if
    set barcode_command to (barcode_script_location & " " & edition_date)
else if barcode_choice is "Special sequence" then
    set barcode_sequence to text returned of (display dialog "Please enter the barcode sequence:" default answer "")
    set barcode_week to text returned of (display dialog "Please enter the barcode week number:" default answer "")
    set barcode_header to text returned of (display dialog "Please enter the barcode header line (24 characters maximum):" default answer "")
    set barcode_command to (barcode_script_location & " direct --seq " & barcode_sequence & " --week " & barcode_week & " --header '" & barcode_header & "'")
end if

set barcode_file_location to ((do shell script barcode_command) as POSIX file)

tell application "Adobe InDesign CS4"
    tell the active document
        place barcode_file_location on page item "Barcode"
        activate
    end tell
end tell
