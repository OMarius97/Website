const d = new Date();
start = d.getSeconds();
end = start + 7


function display(list,seconds){
    document.getElementById("display").innerHTML = list;
    setTimeout(vanish, seconds * 1000)

}

function vanish(){
    document.getElementById("vanish").style.visibility = "hidden"
    document.getElementById("hideout").style.display = ""
}
