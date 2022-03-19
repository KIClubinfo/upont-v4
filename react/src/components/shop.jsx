import React from 'react'
import {StudentsSearchBar, AlcoholsSearchBar} from './searchBars';


class LastTransactions extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return <p></p>;
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
        const url = '/api/forms/transactions/add/'
        const csrfmiddlewaretoken = getCookie('csrftoken');
        const requestOptions = {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': csrfmiddlewaretoken},
            body: JSON.stringify({'good': this.state.alcohol.value, 'student': this.state.student.value})
        };
        fetch(url, requestOptions)
            .then(this.setState({
                "alcohol": '',
                "student": ''
            }))
            .then(response => console.log('Submitted successfully'))
            .catch(error => console.log('Form submit error', error))
    }

    render() {
        return (
        <form method="post" onSubmit={this.handleSubmit.bind(this)}>
            <StudentsSearchBar parent={this}/>
            <p></p>
            <AlcoholsSearchBar parent={this}/>
            <div className="centered-div"><button className="button green-button" type="submit">Valider la transaction</button></div>
        </form>)
    }
}

export default AddTransaction;