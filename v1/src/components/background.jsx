const BackgroundImage = () => {
    return (
        <div className="absolute top-0 left-0 w-full h-full">
            <img
                className="w-full h-full object-cover opacity-50"
                src="/public/assets/Topographic bg.png"
                alt="background"
            />
        </div>
    );
};

export default BackgroundImage;
