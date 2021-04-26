document.addEventListener("DOMContentLoaded",function(e){
    document.forms["player_info"].reset();

    document.getElementById("play").addEventListener("click", function(e){
        document.getElementById("player_info").style.visibility = "visible";
    });

    document.getElementById("player_info").addEventListener("submit", function(e){
        var name = document.getElementById("sent_name").value;
        var last_error = document.querySelector(".err");
        if (name == ""){
            if (last_error == null){
                var text_error = "<p class='err'>Error! Player's name must be filled in!</p>";
                var error_element = document.createElement("p");
                error_element.innerHTML = text_error;
                this.append(error_element);
            }
            e.preventDefault();
            return;
            
        }else {            
            if (last_error != null){
                last_error.parentNode.removeChild(last_error);
                last_error = null;
            }
        }

        var cash = document.getElementById("cash").value;
        if (cash == "" || cash < 1000){
            var text_error = "<p class='err'>Error! Cash must be greater than €1,000!</p>";
            var error_element = document.createElement("p");
            error_element.innerHTML = text_error;
            this.append(error_element); 
            e.preventDefault();
            return;
        }else {
            if (last_error != null){
                last_error.parentNode.removeChild(last_error);            
            }
        }        

        document.getElementById("name").innerHTML = name + ":";

        document.querySelectorAll(".instruction").forEach(function(element){
            element.disabled = false;
        });

        document.getElementById("play").disabled = true;
        
        this.childNodes.forEach(function(element){
            element.disabled = true;
        });
        
        e.preventDefault();
    });

    function disable_instructors(){
        document.querySelectorAll(".instruction").forEach(function(element){
            element.disabled = true;
        });
    }

    disable_instructors();
});