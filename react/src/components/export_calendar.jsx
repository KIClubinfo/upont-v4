import React, { useState } from 'react';

export default function ExportCalendar() {
  const [expanded, setExpanded] = useState(false);
  const [enableExport, setEnableExport] = useState(false);

  const handleExpandeButton = () => {
    setExpanded((prev) => setExpanded(!prev));
  };

  const handleFileformat = (event) => {
    if (event.target.value === '' && enableExport) {
      setEnableExport(false);
    } else if (event.target.value !== '' && !enableExport) {
      setEnableExport(true);
    }
  };

  if (expanded) {
    return (
      <>
        <button
          onClick={handleExpandeButton}
          type="button"
          className="button-drawer"
        >
          <i className="fa fa-arrow-circle-down" />
          Exporter
        </button>
        <form
          method="get"
          // eslint-disable-next-line no-undef
          action={Urls['theCalendar:downloadSchedule']()}
          className="calendar-export-form"
        >
          <select
            name="fileformat"
            id="fileformat"
            className="profil-select"
            defaultValue=""
            onChange={handleFileformat}
            required
          >
            <option value="">Choisir un type de fichier</option>
            <option value="ics">ICS (Iphone, Mac, Ubuntu)</option>
            <option value="csv">CSV (Google Agenda, Outlook)</option>
          </select>
          {enableExport ? (
            <button type="submit" className="button green-button">
              Télécharger l'export
            </button>
          ) : (
            <button type="submit" className="button disabled-button" disabled>
              Télécharger l'export
            </button>
          )}
        </form>
      </>
    );
  }

  return (
    <button
      onClick={handleExpandeButton}
      type="button"
      className="button-drawer"
    >
      <i className="fa fa-arrow-circle-right" />
      Exporter
    </button>
  );
}
