/* eslint-disable react/prop-types */
/* eslint-disable max-classes-per-file */
import React from 'react';
import AsyncSelect from 'react-select/async';

function searchStudent(inputValue) {
  return new Promise((resolve, reject) => {
    // eslint-disable-next-line no-undef
    fetch(`${Urls.search_students()}?user=${inputValue}`)
      .then((response) => response.json())
      .then(({ students }) => {
        resolve(
          students.map(({ id, user, promo }) => ({
            value: id,
            label: `${user.first_name} ${user.last_name} ('${promo.nickname})`,
          })),
        );
      })
      .catch(reject);
  });
}

class StudentsSearchBar extends React.Component {
  customStyles = {
    option: (provided) => ({
      ...provided,
      color: 'black',
    }),
    control: (provided) => ({
      ...provided,
      color: 'black',
    }),
  };

  handleChange = (selectedOption) => {
    this.props.parent.setState({ student: selectedOption });
  };

  render() {
    return (
      <AsyncSelect
        styles={this.customStyles}
        cacheOptions
        defaultOptions
        name="student"
        loadingMessage={() => 'Chargement'}
        onChange={this.handleChange}
        placeholder="Sélectionner un élève"
        loadOptions={searchStudent}
        value={this.props.parent.state.student}
      />
    );
  }
}

function searchAlcohol(inputValue) {
  return new Promise((resolve, reject) => {
    // eslint-disable-next-line no-undef
    fetch(`${Urls.search_alcohols()}?alcohol=${inputValue}`)
      .then((response) => response.json())
      .then(({ alcohols }) => {
        resolve(
          alcohols.map(({ name, degree, volume, price, id }) => ({
            value: id,
            label: `${name} (${volume}mL - ${degree}% - ${(price / 100).toFixed(
              2,
            )} €})`,
          })),
        );
      })
      .catch(reject);
  });
}

class AlcoholsSearchBar extends React.Component {
  customStyles = {
    option: (provided) => ({
      ...provided,
      color: 'black',
    }),
    control: (provided) => ({
      ...provided,
      color: 'black',
    }),
  };

  handleChange = (selectedOption) => {
    this.props.parent.setState({ alcohol: selectedOption });
  };

  render() {
    return (
      <AsyncSelect
        styles={this.customStyles}
        cacheOptions
        defaultOptions
        name="alcohol"
        loadingMessage={() => 'Chargement'}
        onChange={this.handleChange}
        placeholder="Sélectionner une consommation"
        loadOptions={searchAlcohol}
        value={this.props.parent.state.alcohol}
      />
    );
  }
}

export { StudentsSearchBar, AlcoholsSearchBar };
