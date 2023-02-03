import React, { useState } from 'react';

export default function ExportCalendar() {
  const [expanded, setExpanded] = useState(false);

  const handleExpandeButton = () => {
    setExpanded((prev) => setExpanded(!prev));
  };

  if (expanded) {
    return (
      <>
        <button onClick={handleExpandeButton} type="button">
          Exporter
        </button>
        <form
          method="get"
          // eslint-disable-next-line no-undef
          action={Urls['theCalendar:downloadSchedule']()}
        >
          <fieldset>
            <legend>Format de fichier</legend>
            <label>
              CSV (Google Agenda, Outlook)
              <input type="radio" name="fileformat" value="csv" required />
            </label>
            <br />
            <label>
              ICS (Iphone, Mac, Ubuntu)
              <input type="radio" name="fileformat" value="ics" />
            </label>
            <br />
          </fieldset>
          <button type="submit">Télécharger l'export</button>
        </form>
      </>
    );
  }

  return (
    <button onClick={handleExpandeButton} type="button">
      Exporter
    </button>
  );
}
