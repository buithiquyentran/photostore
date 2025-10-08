// Component nhóm label + input
const FormGroup = ({
  label,
  id,
  type = "text",
  value,
  onChange,
  onKeyDown,
  children,
  className,
}: {
  label: string;
  id: string;
  type?: string;
  value?: string;
  className?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  children?: React.ReactNode;
  onKeyDown?: (e: React.KeyboardEvent<HTMLInputElement>) => void;
}) => (
  <div className={`m-0 p-0 w-full ${className}`}>
    <div className="flex justify-between">
      <label htmlFor={id} className="text-primary text-[14px] md:text-[16px]">
        {label}
      </label>
      {children}
    </div>
    <input
      id={id}
      name={id}
      type={type}
      value={value}
      onChange={onChange}
      onKeyDown={onKeyDown}
      className=" text-primary  font-normal w-full focus:outline-none focus:ring-0
   bg-transparent h-8 md:h-14 border border-gray-400 rounded-xl mt-1 px-[10px] py-14px md:px-5"
    />
  </div>
);

export default FormGroup;
