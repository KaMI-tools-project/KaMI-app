/**
 * Handle text file drag and drop on text area and set said text area with file content
 * @param  {Event} event Handle drag and drop event
 * @return {Void}
 */
function dropHandler(event) {
  // Prevent file from being opened by web browser (default behavior)
  event.preventDefault()

  // Get drop zone id
  let dropId = event.target.id;
  let textArea = document.getElementById(dropId);

  // Initiating new FileReader object
  const reader = new FileReader();
  // Create EventListener for setting text area value
  reader.addEventListener("load", (e) => {
  // Set text area value with text file content
  // Reinitialise text area when a new file is dropped
  // TODO: When text file ends with an empty line, event adds an additional empty line in text area after drop.
  // TODO: Text verification needs to be coded
  // Otherwise, when text file has only one line, no new line is added to text area
      textArea.value = e.target.result;
  }, false);

  // Use dataTransfer for interacting with file
  if (event.dataTransfer.items) {
    // Use DataTransferItemList to interact with file(s)
    for (var i = 0; i < event.dataTransfer.items.length; i++) {
      // Check if dropped item(s) is/are file(s) and of mime type 'text/plain'
      if (event.dataTransfer.items[i].kind === 'file' && event.dataTransfer.items[i].type === 'text/plain') {
        // Store file in a variable
        let file = event.dataTransfer.items[i].getAsFile();
        // If file exists, triggers reader event
        if (file) {
          // Default encoding : UTF-8
            reader.readAsText(file);
        }
      }
    }
  }
}
