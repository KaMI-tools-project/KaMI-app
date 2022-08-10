"use strict";

const formOptions             = document.querySelector("#options-form-compare");
let compareBtn                = document.querySelector('#compare-btn');
let metricsDashboardContainer = document.querySelector("#metrics-dashboard-container");
let vtContainer               = document.querySelector("#main-vt-container");
const inputExactMatch         = document.querySelector("#exact-match");
const inputInsert             = document.querySelector("#insertion");
const inputDelSubts           = document.querySelector("#delSubts");

function showHideSpinner() {
    let spinnerLoad = document.querySelector("#spinner-compare");

    const currentState = () => {
        spinnerLoad.style['display'] = "none";
        document.querySelector('#message-compare-btn').textContent = " Compare";
        compareBtn.removeAttribute('disabled');
    }

    const loadState = () => {
        spinnerLoad.style['display'] = "";
        document.querySelector('#message-compare-btn').textContent = " Release the Kraken...! 🐙";
        compareBtn.setAttribute('disabled', "true");
    }

    return (spinnerLoad.style['display'] === "none") ? loadState() : currentState()
}


function getTextAreaValue() {
    return [document.querySelector('#reference').value,
            document.querySelector('#prediction').value];
}


function serializeFormData(reference, prediction) {
    let inputs = formOptions.getElementsByTagName('input');
    let data = {
        reference: reference,
        prediction: prediction,
        preprocessingOpts: "",
        vtOpt:0
    };

    Object.values(inputs).forEach(input =>{
        input.checked
            ? input.name !== "optVT"
                ? data.preprocessingOpts += input.value
                : data.vtOpt = 1
            : input;
    });

    return data
}

function tabulate(columns, scores){
    let table = d3.select('#table-result-container').append('table').attr('class', 'dataframe data table table-hover table-bordered');
    let thead = table.append('thead');
    let tbody = table.append('tbody');
    // append the header row
    thead.append('tr').selectAll('th').data(columns).enter().append('th').text(function (column) {
        return column;
    });
    let rows = tbody.selectAll('tr').data(scores).enter().append('tr');
    // create a cell in each row for each column
    rows.selectAll('td').data(function (row, i) {
        return row;
    }).enter().append('td').html(function (d) {
        if ((typeof d === "string") && (d !== "Ø")) {
            d = "<b>" + d + "</b>";
        }
        return d;
    });
}

function populateVersusText(reference, comparaison, prediction){
    [{reference:reference}, {comparaison: comparaison}, {prediction: prediction}].forEach(version => {
        document.querySelector(`#vt-${Object.keys(version)[0]}`).innerHTML = Object.values(version)[0].join('');
    });
}

function versusTextSelector(){
    [inputExactMatch, inputInsert, inputDelSubts].forEach(btn => {
        btn.addEventListener('click', function (event) {
            document.querySelectorAll("."+event.target.id).forEach(item => {
                (event.target.checked) ? item.classList.remove('clear') : item.classList.add('clear');
            });
        })
    })
}

function fileJSLoader (file, id){
    // remove the old script in header if exists
    try{
        document.querySelector("#"+id).remove();
    }catch (e) {}
    // create a <script> element
    let scriptElement = document.createElement("script");
    // fix attributes
    scriptElement.id   = "dynamic-vt-script";
    scriptElement.type = "text/javascript";
    scriptElement.src  = "static/"+file;
    // add child to <head> tag in DOM
    document.getElementById("head").appendChild(scriptElement);
}

function sendFormToResults() {
    // check if text area are empty : else return submit default validation
    let textAreaValues = getTextAreaValue();
    let reference      = textAreaValues[0];
    let prediction     = textAreaValues[1];
    if (reference !== "" && prediction !== "") {
        // Hide metrics container
        metricsDashboardContainer.style.display = 'none';
        // Hide versus text container
        vtContainer.style.display = 'none';
        // Show spinner
        showHideSpinner();
        // remove previous table if exists
        try{
            document.querySelector('.dataframe').remove();
        }catch (e) {}
        // this part send data to backend
        fetch('/compute_results',{
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            // directly serialize and pass data
            body:JSON.stringify(serializeFormData(reference, prediction))
        })
            .then(response => response.json())
            .then(function (response) {
                tabulate(response.columns, response.scores);
                metricsDashboardContainer.style.display = '';
                if (response.comparaison.length !== 0){
                    populateVersusText(response.reference, response.comparaison, response.prediction)
                    vtContainer.style.display = '';
                    versusTextSelector();
                    // load jquery file to display line VT hover feature (temporary solution, remove and
                    // include here when that is write in full JS
                    fileJSLoader("js/dynamicVT.min.js", "dynamic-vt-script");
                }else{
                    vtContainer.style.display = 'none';
                }
                showHideSpinner("hide");
            }).catch(function(){
            showHideSpinner("hide");
        });
    }
}

compareBtn.addEventListener("click", function () {
    sendFormToResults();
});