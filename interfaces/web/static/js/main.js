document.addEventListener("DOMContentLoaded",function(e){
    document.forms["player_info"].reset();

    function currencyConverter(value){
        const options = {style: "currency", currency:"EUR"};
        const formatter = new Intl.NumberFormat("en-US", options);
        return formatter.format(value);
    }

    function convertCurrency(value){
        return Number(value.replace(/[^0-9.-]+/g,""));
    }

    function toggleClass(element, clas, time){
        function addClass(element, clas){
            element.classList.add(clas);
        }
        function removeClass(element, clas){
            element.classList.remove(clas);
        }
        addClass(element, clas);
        setTimeout(function(){removeClass(element, clas)}, time);
    }

    function startGame(player_name, total_cash, indebtness, num_players){
        var request = new XMLHttpRequest();       
        request.open("POST", "/start", true);
        request.setRequestHeader('Content-Type', "application/json");
        var obj = {name: player_name,
               initial_cash: total_cash,
               allow_debt: indebtness,
               };
        var sent_json = JSON.stringify(obj);
        request.send(sent_json);
    }

    function fillHand(element, array){
        array.forEach(function(item){
            var card = document.createElement("li");
            card.innerHTML = item;
            element.appendChild(card);
        });
    }

    function placeBet(money){
        var request = new XMLHttpRequest();
        request.onreadystatechange = function(){
            if (request.readyState == 4){
                if (request.status == 200){
                    var obj = JSON.parse(request.responseText);
                    var name = document.getElementById("sent_name").value;
                    fillHand(document.getElementById("player_hand"), obj[name])
                    fillHand(document.getElementById("dealer_hand"), obj["Dealer"])
                    }
                }
            }
        
        request.open("POST", "/bet", true);
        request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        request.send( "value=" + money);
    }

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

        startGame(name, cash, document.getElementById("indebtness").value, document.getElementById("num_players").value);
        
        document.getElementById("name").innerHTML = name + ":";

        document.getElementById("play").disabled = true;
        
        this.childNodes.forEach(function(element){
            element.disabled = true;
        });

        var cash_element = document.getElementById("total_cash");
        cash_element.value = currencyConverter(cash);
        toggleClass(cash_element, "high_input_text", 2000);

        document.getElementById("bet_container").style.display = "block";
        toggleClass(document.getElementById("bet_container"), "high_border", 2000);

        e.preventDefault();
    });

    document.getElementById("bet_placer").addEventListener("click", function(e){
        var bet = document.getElementById("bet_value").value;
        var remaining_cash = document.getElementById("total_cash").value;
        var money = convertCurrency(remaining_cash);
        var last_error = document.querySelector(".err");
        
        if (bet < 0 || bet > money || bet == ""){
            if (last_error == null){
                var text_error = "<p class='err'>Error!Bet value must be between €1 and " + remaining_cash + "!</p>";
                var error_element = document.createElement("p");
                error_element.innerHTML = text_error;
                this.parentNode.append(error_element);
            }            
        }else {
            if (last_error != null){
                last_error.parentNode.removeChild(last_error);            
            }

            placeBet(bet);
            
            document.getElementById("total_cash").value = currencyConverter(money - bet);
            document.getElementById("current_bet").value = currencyConverter(bet);
            document.getElementById("bet_value").value = "";
            document.getElementById("bet_container").style.display = "none";

            

            document.querySelectorAll(".instruction").forEach(function(element){
                element.disabled = false;
            });
    

        }
    });

    function resetAll(){
        document.querySelectorAll(".instruction").forEach(function(element){
            element.disabled = true;
        });
        document.getElementById("total_cash").value = "€0.00";
        document.getElementById("current_bet").value = "€0.00";
        document.getElementById("bet_value").value = "";
    }

    resetAll();
});