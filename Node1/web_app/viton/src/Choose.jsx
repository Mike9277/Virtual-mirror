import React, { useState, useEffect } from 'react';
import { css } from '@emotion/react';
import { ClipLoader } from 'react-spinners';
import './css/viton.css';
import useConfig from './config';

export default function Choose() {
  const config = useConfig();
  const [selectedPerson, setSelectedPerson] = useState(null);
  const [selectedCloth, setSelectedCloth] = useState(null);
  const [loading, setLoading] = useState(false);
  const [resultImageUrl, setResultImageUrl] = useState(null);
  const [persons, setPersons] = useState([]);
  

  useEffect(() => {
    if (!config) {
      return;
    }

    const fetchData = async () => {
      try {
        const response = await fetch(`${config.apiUrl}`);
        const data = await response.json();
        setPersons(data);
      } catch (error) {
        console.error('Error fetching images:', error);
      }
    };

    fetchData();
  }, [config]);

  if (!config) {
    return <div>Loading configuration...</div>;
  }

    const handlePersonChange = (e) => {
        setSelectedPerson(e.target.value);
    };

    const handleClothChange = (e) => {
        setSelectedCloth(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setResultImageUrl(null);

        try {
            const response = await fetch(`${config.apiUrl}/run-script_upl`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    person: selectedPerson,
                    cloth: selectedCloth,
                    session_id: sessionId,
                }),
            });
            const data = await response.json();
            console.log(data);
            setResultImageUrl(`data:image/jpeg;base64,${data.image}`);
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    const override = css`
        display: block;
        margin: 0 auto;
        border-color: red;
    `;

    return (
        <div className="choose">
            <form onSubmit={handleSubmit}>
                <div>
                    <p>Choose a person</p>
                    {persons.map((person, index) => [
                        <input key={index} type="radio" id={`person${index}`} name="person" value={person} onChange={handlePersonChange} />,
                        <label key={`label${index}`} htmlFor={`person${index}`}><img src={`/images/${person}`} alt={`Person ${index + 1}`} /></label>
                    ])}
                   
                    <p>Choose a cloth</p>
                    <input type="radio" id="cloth1" name="cloth" value="01260_00.jpg" onChange={handleClothChange} />
                    <label htmlFor="cloth1"><img src="/images/01260_00.jpg" alt="Cloth 1" /></label>

                    <input type="radio" id="cloth2" name="cloth" value="01430_00.jpg" onChange={handleClothChange} />
                    <label htmlFor="cloth2"><img src="/images/01430_00.jpg" alt="Cloth 2" /></label>

                    <input type="radio" id="cloth3" name="cloth" value="02783_00.jpg" onChange={handleClothChange} />
                    <label htmlFor="cloth3"><img src="/images/02783_00.jpg" alt="Cloth 3" /></label>

                    <input type="radio" id="cloth4" name="cloth" value="03751_00.jpg" onChange={handleClothChange} />
                    <label htmlFor="cloth4"><img src="/images/03751_00.jpg" alt="Cloth 4" /></label>
                    </div>
                
                <button type="submit" disabled={loading}>
                    {loading ? 'Loading...' : 'RUN'}
                </button>
            </form>
            <div className="loader-container">
            {loading && <ClipLoader css={override} size={35} color={"#123abc"} loading={loading} />}
            </div>
            <div className="image-container">
            {resultImageUrl && <img id="img_result" src={resultImageUrl} alt="Result" />}
            </div>
        </div>
    );
}
