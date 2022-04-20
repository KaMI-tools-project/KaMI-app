const ReferenceInput          = document.querySelector('#reference');
const PredictionInput         = document.querySelector('#prediction');

const areaNormalShadow        = "0 0 10px var(--white-main)";
const areaSuccessShadow       = "0 0 10px green";
const areaErrorShadow         = "0 0 10px red";

const areaPlaceHolderMsgError = "Only raw text (.txt) are valid, please retry.";
const referencePlaceHolder    = "Drag & Drop or Paste the expected transcription...";
const predictionPlaceHolder   = "Drag & Drop or Paste the transcription produced by the model you wish to evaluate...";

// Global loop to add event listener on inputs (textarea)
[ReferenceInput, PredictionInput].forEach(item => {
    item.addEventListener('drop', event => {
        dropHandler(event);
    });
    item.addEventListener('input',  function (){
        AreaStateShadow(item, 'normal');
        AreaPlaceHolderState(item, item.id, 'normal')
        if (item.value !== ""){
            AreaStateShadow(item, 'success');
        }
    })
})

/**
 * Change border shadow color in relation to input
 * @param  {element} element Input element where border shadow change
 * @param  {string} type Output level desire
 * @return {undefined}
 */
function AreaStateShadow(element, type) {
    element.style["boxShadow"] = areaNormalShadow;
    if (type==='error'){
        element.style["boxShadow"] = areaErrorShadow;
    }if (type==='success'){
        element.style["boxShadow"] = areaSuccessShadow;
    }
}

/**
 * Change placeholder message in input in relation to input
 * @param {element} element Input element where placeholder change
 * @param {string} id ID of input element (textarea)
 * @param {string} type Output level desire
 * @return {undefined}
 */
function AreaPlaceHolderState(element, id, type='normal'){
    if (type === 'normal'){
        if (id === 'reference'){
            element.placeholder    = referencePlaceHolder;
        }if (id === 'prediction'){
            element.placeholder    = predictionPlaceHolder;
        }
    }if(type==='error'){
        element.value = '';
        element.placeholder = areaPlaceHolderMsgError;
    }
}

/**
 * Handle text file drag and drop on text area and set said text area with file content
 * @param  {Event} event Handle drag and drop event
 * @return {undefined}
 */
function dropHandler(event) {
    // Prevent file from being opened by web browser (default behavior)
    event.preventDefault();

    // Get drop zone id
    let dropId = event.target.id;
    let textArea = document.getElementById(dropId);

    // Initiating new FileReader object
    const reader = new FileReader();

    // Get content information from input event
    let dropEvent         = event.dataTransfer.items;
    let dropEventMimetype = dropEvent[0].type;
    let dropEventFormat   = dropEvent[0].kind;

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
    if (dropEvent){
        if (dropEventFormat === 'file' && dropEventMimetype === 'text/plain'){
            let file = dropEvent[0].getAsFile();
            reader.readAsText(file);
            AreaStateShadow(textArea, 'success')
            AreaPlaceHolderState(textArea, dropId, 'normal')
        }
        else{
            AreaStateShadow(textArea, 'error')
            AreaPlaceHolderState(textArea, dropId, 'error')
        }
    }
}