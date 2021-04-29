document.addEventListener("DOMContentLoaded",function(e){
    //Reset File functions
    document.forms["player_info"].reset();
   
    function resetAll(){
        document.querySelectorAll(".instruction").forEach(function(element){
            element.disabled = true;
        });
        document.getElementById("total_cash").value = "€0.00";
        document.getElementById("current_bet").value = "€0.00";
        document.getElementById("bet_value").value = "";
    }
    resetAll();
    //Reset File functions - END
    //Common functions
    function removeChildren(node){
        while (node.firstChild){
            node.removeChild(node.firstChild);
        }
    }

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

    function fillHand(element, array){
        array.forEach(function(item){
            var card = document.createElement("li");
            card.innerHTML = item;
            element.appendChild(card);
        });
    }

    function toggleBetContainer(){
        var container = document.getElementById("bet_container");
        if (container.style.display == "none" || container.style.display == ""){
            container.style.display = "block";
            toggleClass(container, "high_border", 2000);
        }else{
            document.getElementById("bet_value").value = "";
            container.style.display = "none";
        }
    }

    function toggleError(expression, parent, message, cls){
        var last_error = parent.querySelector(".err." + cls);
        if (expression){
            if (last_error == null){
                var text_error = "<p class='err " + cls + "'>" + message + "</p>";
                var error_element = document.createElement("p");
                error_element.innerHTML = text_error;
                parent.append(error_element);              
                
            }

            return true;

        }else {            
            if (last_error != null){
                last_error.parentNode.removeChild(last_error);
                last_error = null;
            }
        }
        return false;
    }

    //Common functions - END
    //AJAX Functions
    function sendInfo(method, url, async, data, callback){
        var request = new XMLHttpRequest();
        request.onreadystatechange = function(){
            if (request.readyState == 4){
                if (request.status == 200){
                    callback(request.responseText);
                }
            }
        }

        request.open(method, url, async);
        request.send(data);
    }

    function BuildForm(obj){
        var data = new FormData();
        const ks = Object.keys(obj);
        ks.forEach((key, index)=>{data.append(key, obj[key]);});
        return data;
    }
    //Ajax Functions - END
    //Events
    //Play!
    document.getElementById("play").addEventListener("click", function(e){
        document.getElementById("player_info").style.visibility = "visible";
    });
    //Start!
    document.getElementById("player_info").addEventListener("submit", function(e){
        var name = document.getElementById("sent_name").value;
        var cash = document.getElementById("cash").value;

        if(toggleError(name=="", e.target, "Error! Player's name must be filled in!", "name")){
            e.preventDefault();
            return;
        }

        if (toggleError((cash == "" || cash < 1000 || isNaN(cash)), e.target,"Error! Cash must be greater than €1,000!", "cash")) {
            e.preventDefault();
            return;
        }

        sendInfo("POST", "/start", false, BuildForm({name: name, initial_cash: cash, 
                                                     allow_debt: document.getElementById("indebtness").value}),
                 (text)=>{});

        
        document.getElementById("name").innerHTML = name + ":";

        document.getElementById("play").disabled = true;
        
        this.childNodes.forEach(function(element){
            element.disabled = true;
        });

        var cash_element = document.getElementById("total_cash");
        cash_element.value = currencyConverter(cash);
        toggleClass(cash_element, "high_input_text", 2000);


        toggleBetContainer();

        e.preventDefault();
    });
    //Place Bet
    document.getElementById("bet_placer").addEventListener("click", function(e){
        var bet = document.getElementById("bet_value").value;
        var remaining_cash = document.getElementById("total_cash").value;
        var money = convertCurrency(remaining_cash);
        var debt = document.getElementById("indebtness").value;
        var evaluation = (bet < 0 || bet == "" || (bet > money && debt =="N"));

        if (!toggleError(evaluation, e.target.parentNode, "Bet value must be between €1 and " + remaining_cash, "bet")){
            sendInfo("POST", "/bet", false, BuildForm({value: bet}),(text)=>{
                    var obj = JSON.parse(text);
                    var name = document.getElementById("sent_name").value;
                    fillHand(document.getElementById("player_hand"), obj[name])
                    fillHand(document.getElementById("dealer_hand"), obj["Dealer"])
            } );
            
            document.getElementById("total_cash").value = currencyConverter(money - bet);
            document.getElementById("current_bet").value = currencyConverter(bet);
            toggleBetContainer();
            

            document.querySelectorAll(".instruction").forEach(function(element){
                element.disabled = false;
            });  

        }
    });

    //Hit & Stand
    document.querySelectorAll(".instruction").forEach(function(element){
        element.addEventListener("click", function(e){
            sendInfo("POST", "/action", false, BuildForm({action: e.target.value}), (text)=>{
                var obj = JSON.parse(text);
                var player = document.getElementById("player_hand");
                var name = document.getElementById("sent_name").value;
                var dealer = document.getElementById("dealer_hand");
                if (obj["Status"] == "on"){
                    removeChildren(player);
                    fillHand(player, obj[name]);
                } else {
                    removeChildren(dealer);
                    fillHand(dealer, obj["Dealer"]);                            
                    document.querySelectorAll(".instruction").forEach(function(element){
                        element.disabled = true;
                    });

                    var status_message = "<p class='err'>" + obj["Status"] + "</p>";
                    var message = document.createElement("p");
                    message.innerHTML = status_message;
                    player.parentNode.append(message);
                    
                    setTimeout(function(){
                        removeChildren(player);
                        removeChildren(dealer);
                        player.parentNode.removeChild(message);
                        toggleBetContainer();
                    }, 5000);                    
                }})
        });
    });
});