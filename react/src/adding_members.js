import ReactDOM from 'react-dom'
import React from 'react'
import AsyncSelect from 'react-select/async';

const customStyles = {
    option: provided => ({
        ...provided,
        color: 'black'
    }),
    control: provided => ({
        ...provided,
        color: 'black'
    }),
}

ReactDOM.render((<AsyncSelect styles={customStyles} cacheOptions defaultOptions name="student"
                              loadOptions={get_student}/>), document.getElementById('adding_student'))
ReactDOM.render((<AsyncSelect styles={customStyles} cacheOptions defaultOptions name="role"
                              loadOptions={get_roles}/>), document.getElementById('adding_role'))

function get_student(inputValue) {
    return new Promise((resolve, reject) => {
        fetch(`/api/search/students/?user=${inputValue}`)
            .then(response => response.json())
            .then(({students}) => {
                resolve(students.map(({id, user, promo}) => ({
                    value: id,
                    label: `${user.first_name} ${user.last_name} ('${promo.nickname})`
                })))
            })
            .catch(reject);
    });
}


function get_roles(query) {
    return new Promise((resolve, reject) => {
        fetch(`/api/search/roles/?role=${query}`)
            .then(response => response.json())
            .then(({roles}) => {
                resolve(roles.map(({id, name}) => ({label: name, value: id})))
            })
            .catch(reject);
    });
}
