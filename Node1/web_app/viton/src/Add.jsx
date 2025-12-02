import React, { useState } from 'react';
import { css } from '@emotion/react';
import { ClipLoader } from 'react-spinners';
import { Element, scroller } from 'react-scroll';
import './css/viton.css';
import useConfig from './config';

export default function Add() {
    const [loading, setLoading] = useState(false);
    const [file, setFile] = useState(null);
    const [imageSrc, setImageSrc] = useState(null);
    const [progress, setProgress] = useState(0);
    const [filename, setFilename] = useState('');
    const [preprocessFinished, setPreprocessFinished] = useState('Preprocess');
    const [buttonClassName, setButtonClassName] = useState('button_preprocess');
    const [data_prepro, setDataPrepro] = useState(null);
    const [clothImages, setClothImages] = useState([]);
    const [vitontest, setVitontest] = useState(null);
    const [selectedCloth, setSelectedCloth] = useState(null);
    const [resultImageUrl, setResultImageUrl] = useState(null);
    const [sessionId, setSessionId] = useState(null);
    const config = useConfig();
    //
    const [jetsonFiles, setJetsonFiles] = useState([]);
    const [selectedFile, setSelectedFile] = useState('');
    //
    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile.type !== 'image/jpeg') {
            alert("Please select a .jpg file.");
            e.target.value = null;
            return;
        }
        setFile(selectedFile);
    };

    const handleSelectChange = (e) => {
        setSelectedFile(e.target.value);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setProgress(0);
        setPreprocessFinished("Click here for preprocessing");
        setButtonClassName('button_preprocess');

        const formData = new FormData();
        formData.append('image', file);

        try {
            const response = await fetch(`${config.apiUrl}/add-img`, {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();
            if (data.image) {
                setImageSrc(`data:image/jpeg;base64,${data.image}`);
                setFilename(data.filename);
            }
        } catch (error) {
            console.error('Error:', error);
        } finally {
            setLoading(false);
        }
    };

    const preprocessImage = async (e) => {
        setPreprocessFinished('Preprocessing ...');
        setDataPrepro(null);
        setVitontest(null);
        setResultImageUrl(null);
        setButtonClassName('button_preprocess_inactive');
        e.preventDefault();
        let interval = setInterval(() => {
            setProgress(prevProgress => Math.min(prevProgress + 1, 100));
        }, 500);
        try {
            const response = await fetch(`${config.apiUrl}/preprocess-upl`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ filename }),
            });
            const data = await response.json();

            setSessionId(data.sessionId)
            
            console.log(data);
            setDataPrepro(data);
            setPreprocessFinished('Preprocessing Finished !');
            clearInterval(interval); // Stop the interval when processing is finished
            setProgress(100); // Set progress to 100% immediately
            setTimeout(() => {
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            }, 100);
        } catch (error) {
            console.error('Error:', error);
            clearInterval(interval);
        }
    };
    const handleClothChange = (e) => {
        setSelectedCloth(e.target.value.replace("cloths/", ""));
        
    };
    const addViton = async (e) => {
        e.preventDefault();
        setVitontest(true);
        try {
            const response = await fetch(`${config.apiUrl}/addViton`, {
                method: 'GET',
            });
            const data = await response.json();
            console.log(data);
            setClothImages(data);
            setTimeout(() => {
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            }, 100);
        } catch (error) {
            console.error('Error:', error);
        }

    };
    const RunViton = async (e)=>{
        e.preventDefault();
        console.log("ok : ",selectedCloth," nom : ", filename);
        setLoading(true);
        setResultImageUrl(null);
        try {
            const response = await fetch(`${config.apiUrl}/run-script-upl`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    person: filename,
                    cloth: selectedCloth,
                    sessionId: sessionId,
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
    }
    const override = css`
        display: block;
        margin: 0 auto;
        border-color: red;
    `;

    return (
        <div className="preprocess">
            <div className="choose">
                <form onSubmit={handleSubmit}>
                    <div>
                        <p>Add your image from file :</p>
                        <input type="file" id="myFile" name="filename" onChange={handleFileChange} />
                    </div>
                    <button type="submit" disabled={loading}>
                        {loading ? 'Loading...' : 'Add'}
                    </button>
                </form>

                <div className="image-container">
                    {imageSrc && (
                        <img src={imageSrc} alt="Uploaded" />
                    )}
                </div>
            </div>
            {imageSrc && (
                <button className={buttonClassName} onClick={preprocessImage}>
                    {preprocessFinished}
                </button>
            )}
            {data_prepro && (
                <Element name="images_result">
                    <div className="images_result" id="images_result">
                        <div className="img_from_pre">
                            <h3>Image without background : </h3>
                            <img src={`data:image/jpeg;base64,${data_prepro.original_image}`} alt="original" />
                        </div>
                        <div className="img_from_pre">
                            <h3>OpenPose : </h3>
                            <img src={`data:image/jpeg;base64,${data_prepro.rendered_image}`} alt="openpose" />
                        </div>
                        <div className="img_from_pre">
                            <h3>Human Parsing : </h3>
                            <img src={`data:image/jpeg;base64,${data_prepro.vis_image}`} alt="human parse" />
                        </div>
                    </div>
                    <button className="bouton_test_viton" onClick={addViton} >Test with VITON</button>
                    {vitontest && (
                        <div className="choose centre">
                            <form className="formvitontest">
                                <p>Choose a cloth : </p>
                                <div className="vitontest">
                                    {clothImages.map((image, index) => (
                                        <div>
                                            <input type="radio" id={`cloth${index}`} name="cloth" value={image} onChange={handleClothChange} />
                                            <label htmlFor={`cloth${index}`}><img src={`/images/${image}`} alt={`Cloth ${index + 1}`} /></label>
                                        </div>
                                    ))}
                                </div>
                                <button onClick={RunViton}>Test</button>
                            </form>
                            <div className="loader-container">
                                {loading && <ClipLoader css={override} size={35} color={"#123abc"} loading={loading} />}
                            </div>
                            <div className="image-container">
                                {resultImageUrl && <img id="img_result" src={resultImageUrl} alt="Result" />}
                            </div>
                        </div>
                    )}
                </Element>
            )}
            {preprocessFinished === 'Preprocessing ...' && (
                <div className="progress-bar-container">
                    <div className="progress-bar" style={{ width: `${progress}%` }}></div>
                </div>
            )}
        </div>
    );
}
