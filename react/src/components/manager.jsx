import React from 'react'
import {StudentsSearchBar} from './searchBars';
import {BottomScrollListener} from 'react-bottom-scroll-listener';


class LastTransactionsScroll extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            "transactions": [],
            "start": 0,
            "end": 20,
            "has_more": true,
        };
    }

    componentDidMount() {
        fetch("/api/id/pochtron/")
        .then(res => res.json())
        .then(result => {this.setState({"pochtron_id": result.id})})
        .then(() => this.loadMore())
    }

    loadMore() {
        if (this.state.has_more) {
            fetch("/api/transactions/last/?club="+this.state.pochtron_id+"&start="+this.state.start+"&end="+this.state.end)
            .then(res => res.json())
            .then(
                (result) => {
                    this.setState({
                        "transactions": this.state.transactions.concat(result.transactions),
                        "start": this.state.start + 20,
                        "end": this.state.end + 20,
                        "has_more": result.has_more,
                    })
                },
                (error) => {
                    this.setState({
                        error
                    });
                }
            )
        }
    }

    clear() {
        setTimeout(() =>
            this.setState({
                "transactions": [],
                "start": 0,
                "end": 20,
                "has_more": true,
                },
                () => this.loadMore())
            , 1000);
    }

    render() {
        return (
            <div>
            <BottomScrollListener onBottom={() => this.loadMore()} />
            <hr></hr>
            <h4>Dernières transactions : </h4>
            <table className="table">
                <thead>
                    <tr>
                        <td>Élève</td>
                        <td>Consommation</td>
                        <td>Quantité</td>
                        <td>Date</td>
                    </tr>
                </thead>
                <tbody>
                {
                    this.state.transactions.map(function f(transaction) {
                        return (
                            <tr key={transaction.id}>
                                <td>{transaction.student.user.first_name + " " + transaction.student.user.last_name}</td>
                                <td>{transaction.good.name}</td>
                                <td>{transaction.quantity}</td>
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


class CreditAccount extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            amount: '',
            student: '',
        };
        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleChange = this.handleChange.bind(this);
    }

    componentDidMount() {
        fetch("/api/id/pochtron/")
        .then(res => res.json())
        .then(result => {this.setState({"pochtron_id": result.id})})
    }

    handleChange(event) {
        this.setState({ [event.target.name]: event.target.value });
    }

    handleSubmit(event) {
        event.preventDefault();
        const url = '/api/forms/transactions/credit/'
        const csrfmiddlewaretoken = getCookie('csrftoken');
        const requestOptions = {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfmiddlewaretoken},
            body: JSON.stringify({'club': this.state.pochtron_id, 'student': this.state.student.value, 'amount': this.state.amount})
        };
        fetch(url, requestOptions)
            .then(this.setState({
                "student": '',
                "amount": ''
            }))
            .then(res => res.json())
            .then(response => this.setState({"error": response.error}))
            .catch(error => console.log('Form submit error', error))
        this.props.clear();
    }

    render() {
        return (
        <div>
            <hr></hr>
            <h4>Créditer un compte :</h4>
            <form method="post" onSubmit={this.handleSubmit.bind(this)}>
                <div className="centered-div text-red"><p>{this.state.error}</p></div>
                <p>Élève :</p>
                <StudentsSearchBar parent={this}/>
                <p></p>
                <p>Montant à créditer (centimes) :</p><input className="centered-div text-input white-input" type="text" placeholder="Montant" name="amount" id="" value={this.state.amount} onChange={this.handleChange}></input>
                <div className="centered-div"><button className="button green-button" type="submit">Créditer</button></div>
            </form>
        </div>)
    }
}



class Manager extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            "clear": () => setTimeout(0)
        };
    }

    componentDidMount() {
        this.setState({
            "clear": () => this.LastTransactionsScroll.clear()
        })
    }


    render() {
        return (
            <>
                <CreditAccount clear={() => this.state.clear()} />
                <LastTransactionsScroll ref={instance => { this.LastTransactionsScroll = instance; }}/>
            </>
        )
    }
}

export {Manager};
