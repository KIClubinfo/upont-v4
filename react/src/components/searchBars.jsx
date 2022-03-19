import React from 'react'
import AsyncSelect from 'react-select/async'


class StudentsSearchBar extends React.Component {
    constructor(props) {
        super(props);
    }

    getStudent(inputValue) {
        return new Promise((resolve, reject) => {
          fetch(`/api/search/students/?user=${inputValue}`)
            .then(response => response.json())
            .then(({ students }) => {
              resolve(students.map(({ id, user, promo }) => ({
                value: id,
                label: `${user.first_name} ${user.last_name} ('${promo.nickname})`
              })))
            })
            .catch(reject)
        })
      }

    customStyles = {
        option: provided => ({
          ...provided,
          color: 'black'
        }),
        control: provided => ({
          ...provided,
          color: 'black'
        })
    }

    handleChange = (selectedOption) => {
      this.props.parent.setState({"student": selectedOption});
    }

    render() {
        return <AsyncSelect
            styles={this.customStyles} cacheOptions defaultOptions name='student' loadingMessage={() => 'Chargement'}
            onChange={this.handleChange}
            placeholder='Sélectionner un élève'
            loadOptions={this.getStudent}
            value={this.props.parent.state.student}
        />
    }
}


class AlcoholsSearchBar extends React.Component {
    constructor(props) {
        super(props);
    }

    getAlcohol(inputValue) {
        return new Promise((resolve, reject) => {
          fetch(`/api/search/alcohols/?alcohol=${inputValue}`)
            .then(response => response.json())
            .then(({ alcohols }) => {
              resolve(alcohols.map(({ name, degree, volume, price, id }) => ({
                value: id,
                label: `${name} (${volume}mL - ${degree}% - ${price} centimes)`
              })))
            })
            .catch(reject)
        })
      }

    customStyles = {
        option: provided => ({
          ...provided,
          color: 'black'
        }),
        control: provided => ({
          ...provided,
          color: 'black'
        })
    }

    handleChange = (selectedOption) => {
      this.props.parent.setState({"alcohol": selectedOption});
    }

    render() {
        return <AsyncSelect
            styles={this.customStyles} cacheOptions defaultOptions name='alcohol' loadingMessage={() => 'Chargement'}
            onChange={this.handleChange}
            placeholder='Sélectionner une consommation'
            loadOptions={this.getAlcohol}
            value={this.props.parent.state.alcohol}
        />
    }
}


export {StudentsSearchBar, AlcoholsSearchBar};
