import React from 'react'
import {StudentsSearchBar, AlcoholsSearchBar} from './searchBars';


class LastTransactions extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            "transactions": []
        };
    }

    componentDidMount() {
        fetch(Urls["pochtron_id"]())
        .then(res => res.json())
        .then(result => {this.setState({"pochtron_id": result.id})})
        this.interval = setInterval(() => this.load(), 1000);
    }

    componentWillUnmount() {
        clearInterval(this.interval);
    }

    load() {
        fetch(Urls["last_transactions"]()+"?club="+this.state.pochtron_id)
        .then(res => res.json())
        .then(
            (result) => {
                this.setState({
                    "transactions": result.transactions,
                })
            },
            (error) => {
                this.setState({
                    error
                });
            }
        )
    }

    render() {
        return (
            <div>
            <h4>Dernières transactions : </h4>
            <table className="table">
                <thead>
                    <tr>
                        <td>Élève</td>
                        <td>Consommation</td>
                        <td>Quantité</td>
                        <td>Coût (centimes)</td>
                        <td>Date</td>
                    </tr>
                </thead>
                <tbody>
                {
                    this.state.transactions.map(function f(transaction) {
                        const balance_change = transaction.quantity*transaction.good.price

                        var balance_color;
                        if (balance_change > 0) {
                            balance_color = 'text-red'
                        }
                        else if (balance_change < 0) {
                            balance_color = 'text-green'
                        }
                        else {
                            balance_color = ''
                        }

                        return (
                            <tr key={transaction.id}>
                                <td>{transaction.student.user.first_name + " " + transaction.student.user.last_name}</td>
                                <td>{transaction.good.name}</td>
                                <td>{transaction.quantity}</td>
                                <td className={balance_color}>{balance_change}</td>
                                <td>{transaction.date}</td>
                            </tr>
                        )
                    })
                }
                </tbody>
            </table>
            </div>
        )
    }
}

class AddTransaction extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            alcohol: '',
            student: '',
        };
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleSubmit(event) {
        event.preventDefault();
        const url = Urls["add_transaction"]()
        const csrfmiddlewaretoken = getCookie('csrftoken');
        const requestOptions = {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfmiddlewaretoken},
            body: JSON.stringify({'good': this.state.alcohol.value, 'student': this.state.student.value})
        };
        fetch(url, requestOptions)
            .then(this.setState({
                "alcohol": '',
                "student": '',
                "last_student": this.state.student
            }))
            .then(res => res.json())
            .then(response => this.setState({"error": response.error, "new_balance": response.new_balance}))
            .catch(error => console.log('Form submit error', error))
    }

    render() {
        let last_transaction;
        if ("last_student" in this.state && "error" in this.state && "new_balance" in this.state) {
            // A transaction has been made with the component
            if (this.state.error.length == 0) {
                // The last transaction was successful
                last_transaction =
                <div className="centered-div text-green">
                    <p>Nouveau solde de {this.state.last_student.label} : {this.state.new_balance/100} €</p>
                </div>;
            } else {
                // An error occurred
                last_transaction =
                <div className="centered-div text-red">
                    <p>{this.state.error}</p>
                </div>;
            }
        }

        return (
            <div>
                <form method="post" onSubmit={this.handleSubmit.bind(this)}>
                    {last_transaction}
                    <StudentsSearchBar parent={this}/>
                    <p></p>
                    <AlcoholsSearchBar parent={this}/>
                    <div className="centered-div"><button className="button green-button" type="submit">Valider la transaction</button></div>
                </form>
            </div>
        )
    }
}

export {AddTransaction, LastTransactions};