const inputExactMatch = document.querySelector("#exact-match");
const inputInsert     = document.querySelector("#insertion");
const inputDelSubts   = document.querySelector("#delSubts");

[inputExactMatch, inputInsert, inputDelSubts].forEach(btn => {
    btn.addEventListener('click', function (event) {
        let classname = event.target.id;
        document.querySelectorAll("."+classname).forEach(item => {
            if(event.target.checked){
                item.classList.remove('clear');
            }
            else{
                item.classList.add('clear');
            }

        });

    })
})

