import React from 'react'
import { StudentsSearchBar } from './searchBars'
import { BottomScrollListener } from 'react-bottom-scroll-listener'
import CurrencyInput from './currencyInput'

class LastTransactionsScroll extends React.Component {
  constructor (props) {
    super(props)
    this.state = {
      transactions: [],
      start: 0,
      end: 20,
      has_more: true
    }
  }

  componentDidMount () {
    fetch(Urls.pochtron_id())
      .then(res => res.json())
      .then(result => { this.setState({ pochtron_id: result.id }) })
      .then(() => this.loadMore())
  }

  loadMore () {
    if (this.state.has_more) {
      fetch(Urls.last_transactions() + '?club=' + this.state.pochtron_id + '&start=' + this.state.start + '&end=' + this.state.end)
        .then(res => res.json())
        .then(
          (result) => {
            this.setState({
              transactions: this.state.transactions.concat(result.transactions),
              start: this.state.start + 20,
              end: this.state.end + 20,
              has_more: result.has_more
            })
          },
          (error) => {
            this.setState({
              error
            })
          }
        )
    }
  }

  clear () {
    setTimeout(() =>
      this.setState({
        transactions: [],
        start: 0,
        end: 20,
        has_more: true
      },
      () => this.loadMore())
    , 1000)
  }

  render () {
    return (
      <div>
        <BottomScrollListener onBottom={() => this.loadMore()} />
        <hr />
        <h4>Dernières transactions : </h4>
        <table className='table'>
          <thead>
            <tr>
              <td>Élève</td>
              <td>Consommation</td>
              <td>Quantité</td>
              <td>Coût</td>
              <td>Date</td>
            </tr>
          </thead>
          <tbody>
            {
                    this.state.transactions.map(function f (transaction) {
                      const balanceChange = transaction.quantity * transaction.good.price

                      let balanceColor = 'text-bold'
                      if (balanceChange > 0) {
                        balanceColor += ' text-green'
                      } else if (balanceChange < 0) {
                        balanceColor += ' text-red'
                      } else {
                        balanceColor = ''
                      }

                      return (
                        <tr key={transaction.id}>
                          <td>{transaction.student.user.first_name + ' ' + transaction.student.user.last_name}</td>
                          <td>{transaction.good.name}</td>
                          <td>{transaction.quantity}</td>
                          <td className={balanceColor}>{(balanceChange / 100).toFixed(2)} €</td>
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
  constructor (props) {
    super(props)
    this.state = {
      amount: 0,
      student: ''
    }
    this.handleSubmit = this.handleSubmit.bind(this)
    this.handleChange = this.handleChange.bind(this)
  }

  componentDidMount () {
    fetch(Urls.pochtron_id())
      .then(res => res.json())
      .then(result => { this.setState({ pochtron_id: result.id }) })
  }

  handleChange (event) {
    this.setState({ [event.target.name]: event.target.value })
  }

  handleAmountChange (newAmount) {
    if (typeof newAmount !== 'undefined') {
      this.setState({ amount: newAmount })
    }
  }

  handleSubmit (event) {
    event.preventDefault()
    const url = Urls.credit_account()
    const csrfmiddlewaretoken = getCookie('csrftoken')
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfmiddlewaretoken },
      body: JSON.stringify({ club: this.state.pochtron_id, student: this.state.student.value, amount: this.state.amount })
    }
    fetch(url, requestOptions)
      .then(this.setState({
        student: '',
        amount: 0,
        last_student: this.state.student
      }))
      .then(res => res.json())
      .then(response => {
        this.setState({ error: response.error })

        if ('new_balance' in response) {
          this.setState({ new_balance: response.new_balance })
        }
      }
      ).catch(error => console.log('Form submit error', error))
    this.props.clear()
  }

  render () {
    let lastTransaction
    if ('last_student' in this.state && 'error' in this.state) {
      // A transaction has been made with the component
      if (this.state.error.length === 0) {
        // The last transaction was successful
        lastTransaction = (
          <div className='centered-div text-green'>
            <p>
              Nouveau solde de {this.state.last_student.label} :
              <div className='text-bold'>
                {this.state.new_balance} €
              </div>
            </p>
          </div>
        )
      } else {
        // An error occurred
        lastTransaction = (
          <div className='centered-div text-red'>
            <p>{this.state.error}</p>
          </div>
        )
      }
    }

    return (
      <div>
        <hr />
        <h4>Créditer un compte :</h4>
        <form method='post' onSubmit={this.handleSubmit.bind(this)}>
          {lastTransaction}
          <p>Élève :</p>
          <StudentsSearchBar parent={this} />
          <p />
          <p>Montant à créditer :</p>
          <CurrencyInput
            className='centered-div text-input white-input'
            type='text'
            name='amount'
            id=''
            value={this.state.amount}
            onValueChange={(v) => { this.handleAmountChange(v) }}
          />
          <div className='centered-div'><button className='button green-button' type='submit'>Créditer</button></div>
          <p />
        </form>
      </div>
    )
  }
}

class Manager extends React.Component {
  constructor (props) {
    super(props)
    this.state = {
      clear: () => setTimeout(0)
    }
  }

  componentDidMount () {
    this.setState({
      clear: () => this.LastTransactionsScroll.clear()
    })
  }

  render () {
    return (
      <>
        <CreditAccount clear={() => this.state.clear()} />
        <LastTransactionsScroll ref={instance => { this.LastTransactionsScroll = instance }} />
      </>
    )
  }
}

export { Manager }
