// ---------------------------------------------------------------
// 10-2025, Michelangelo Guaitolini
// AddCamera: Webcam capture + preprocessing + VITON
// ---------------------------------------------------------------

import React, { useState, useRef, useEffect } from "react";
import { css } from "@emotion/react";
import { ClipLoader } from "react-spinners";
import { Element } from "react-scroll";
import "./css/viton.css";
import useConfig from "./config";

export default function AddCamera() {
    const config = useConfig();
    const [loading, setLoading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [dataPrepro, setDataPrepro] = useState(null);
    const [resultImageUrl, setResultImageUrl] = useState(null);
    const [clothImages, setClothImages] = useState([]);
    const [vitontest, setVitontest] = useState(false);
    const [selectedCloth, setSelectedCloth] = useState(null);
    const [sessionId, setSessionId] = useState(null);

    const videoRef = useRef(null);
    const canvasRef = useRef(null);

    const override = css`
    display: block;
    margin: 0 auto;
    border-color: red;
  `;

    // ----------------------------
    // 1. Start webcam
    // ----------------------------
    useEffect(() => {
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            alert("Camera not supported or HTTPS missing");
            return;
        }
        navigator.mediaDevices
            .getUserMedia({ video: true })
            .then((stream) => {
                videoRef.current.srcObject = stream;
            })
            .catch((err) => console.error("Error accessing webcam:", err));
    }, []);

    // ----------------------------
    // 2. Capture picture
    // ----------------------------
    const takePicture = (e) => {
        e.preventDefault();
        const canvas = canvasRef.current;
        const video = videoRef.current;
        if (!canvas || !video) return;

        const boxWidth = video.clientWidth;
        const boxHeight = video.clientHeight;
        const videoWidth = video.videoWidth;
        const videoHeight = video.videoHeight;

        const scale = Math.max(boxWidth / videoWidth, boxHeight / videoHeight);
        const scaledWidth = videoWidth * scale;
        const scaledHeight = videoHeight * scale;

        const offsetX = (scaledWidth - boxWidth) / 2;
        const offsetY = (scaledHeight - boxHeight) / 2;

        canvas.width = boxWidth;
        canvas.height = boxHeight;
        const ctx = canvas.getContext("2d");

        ctx.save();
        ctx.scale(-1, 1); // mirror
        ctx.drawImage(video, -scaledWidth + offsetX, -offsetY, scaledWidth, scaledHeight);
        ctx.restore();

        const dataURL = canvas.toDataURL("image/jpeg");
        setResultImageUrl(dataURL);
        setDataPrepro(null);
        setVitontest(false);
        setClothImages([]);
        setSelectedCloth(null);
    };

    // ----------------------------
    // 3. Preprocess image
    // ----------------------------
    const preprocessImage = async (e) => {
        e.preventDefault();
        if (!resultImageUrl) return;

        setLoading(true);
        setProgress(0);

        const interval = setInterval(() => {
            setProgress((prev) => Math.min(prev + 1, 100));
        }, 500);

        try {
            const response = await fetch(`${config.apiUrl}/preprocess-img`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ image_data: resultImageUrl }),
            });

            const data = await response.json();
            console.log("Preprocess result:", data);

            if (data.error) {
                alert(`Preprocess failed: ${data.error}`);
            } else {
                setDataPrepro(data);
                setSessionId(data.sessionId || null);
            }
        } catch (err) {
            console.error("Error:", err);
        } finally {
            clearInterval(interval);
            setProgress(100);
            setLoading(false);
            setTimeout(() => window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" }), 100);
        }
    };

    // ----------------------------
    // 4. VITON workflow
    // ----------------------------
    const addViton = async (e) => {
        e.preventDefault();
        setVitontest(true);
        try {
            const response = await fetch(`${config.apiUrl}/addViton`);
            const data = await response.json();
            setClothImages(data);
        } catch (err) {
            console.error("Error fetching clothes:", err);
        }
    };

    const handleClothChange = (e) => setSelectedCloth(e.target.value.replace("cloths/", ""));

    const runViton = async (e) => {
        e.preventDefault();
        if (!selectedCloth || !dataPrepro) return;

        setLoading(true);
        try {
            const response = await fetch(`${config.apiUrl}/run-script`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    image_data: resultImageUrl,
                    cloth: selectedCloth,
                    sessionId,
                }),
            });

            const data = await response.json();
            if (data.image) setResultImageUrl(`data:image/jpeg;base64,${data.image}`);
        } catch (err) {
            console.error("Error running VITON:", err);
        } finally {
            setLoading(false);
        }
    };

    // ----------------------------
    // 5. Render
    // ----------------------------
    return (
        <div className="preprocess">
            <form className="formCapture">
                <button className="bouton_test_viton" onClick={takePicture}>
                    Take a picture
                </button>
            </form>

            <div className="camera_picture">
                {/* Live webcam */}
                <div className="image-container margin0">
                    <video
                        ref={videoRef}
                        autoPlay
                        playsInline
                        muted
                        width="100%"
                        height="100%"
                        style={{ border: "1px solid #ccc", objectFit: "cover", transform: "scaleX(-1)" }}
                    />
                </div>

                {/* Captured image */}
                <div className="image-container">
                    {resultImageUrl && <img src={resultImageUrl} alt="capture" />}
                    {loading && <ClipLoader css={override} size={35} color="#123abc" loading />}
                </div>
            </div>

            {resultImageUrl && (
                <button className="button_preprocess" onClick={preprocessImage}>
                    Preprocess
                </button>
            )}

            {loading && (
                <div className="progress-bar-container">
                    <div className="progress-bar" style={{ width: `${progress}%` }}></div>
                </div>
            )}

            {dataPrepro && (
                <Element name="images_result">
                    <div className="images_result">
                        <div className="img_from_pre">
                            <h3>Image without background:</h3>
                            <img src={`data:image/jpeg;base64,${dataPrepro.original_image}`} alt="original" />
                        </div>
                        <div className="img_from_pre">
                            <h3>OpenPose:</h3>
                            <img src={`data:image/jpeg;base64,${dataPrepro.rendered_image}`} alt="openpose" />
                        </div>
                        <div className="img_from_pre">
                            <h3>Human Parsing:</h3>
                            <img src={`data:image/jpeg;base64,${dataPrepro.vis_image}`} alt="human parse" />
                        </div>
                    </div>

                    <button className="bouton_test_viton" onClick={addViton}>
                        Test with VITON
                    </button>

                    {vitontest && (
                        <div className="choose centre">
                            <form className="formvitontest">
                                <p>Choose a cloth:</p>
                                <div className="vitontest">
                                    {clothImages.map((image, index) => (
                                        <div key={index}>
                                            <input
                                                type="radio"
                                                id={`cloth${index}`}
                                                name="cloth"
                                                value={image}
                                                onChange={handleClothChange}
                                            />
                                            <label htmlFor={`cloth${index}`}>
                                                <img src={`/images/${image}`} alt={`Cloth ${index + 1}`} />
                                            </label>
                                        </div>
                                    ))}
                                </div>
                                <button onClick={runViton}>Test</button>
                            </form>
                            <div className="image-container">
                                {resultImageUrl && <img src={resultImageUrl} alt="Result" />}
                            </div>
                            {loading && <ClipLoader css={override} size={35} color="#123abc" loading />}
                        </div>
                    )}
                </Element>
            )}

            <canvas ref={canvasRef} style={{ display: "none" }} />
        </div>
    );
}
